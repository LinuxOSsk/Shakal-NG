# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
from collections import namedtuple
from datetime import datetime
from os import path

import pytz
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand
from django.db import transaction, connections
from django.utils.functional import cached_property

from ...models import Term, Node, NodeRevision, File
from accounts.models import User
from blackhole.models import VocabularyNodeType


#from common_utils.asciitable import NamedtupleTablePrinter


COMMENT_NODE_HIDDEN = 0
COMMENT_NODE_CLOSED = 1
COMMENT_NODE_OPEN = 2

NODE_NOT_PROMOTED = 0
NODE_PROMOTED = 1

NODE_NOT_STICKY = 0
NODE_STICKY = 1

USER_STATUS_BLOCKED = 0
USER_STATUS_ACTIVE = 1


FilterFormat = namedtuple('FilterFormat', ['format', 'name'])
NodeData = namedtuple('NodeData', ['nid', 'type', 'title', 'uid', 'status', 'created', 'changed', 'comment', 'promote', 'sticky', 'vid', 'revisions', 'terms'])
NodeRevisionData = namedtuple('NodeRevisionData', ['nid', 'vid', 'uid', 'title', 'body', 'teaser', 'timestamp', 'format', 'log'])
TermData = namedtuple('TermData', ['tid', 'parent', 'vid', 'name', 'description'])
UserData = namedtuple('UserData', ['uid', 'name', 'signature', 'created', 'login', 'status', 'picture'])
FileData = namedtuple('FileData', ['fid', 'nid', 'filename', 'filepath', 'filemime', 'filesize'])


FORMATS_TRANSLATION = {
	'Filtered HTML': 'html',
	'PHP code': 'html',
	'Full HTML': 'raw',
	'No HTML': 'text',
}


def timestamp_to_time(timestamp):
	return datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)


def dot():
	sys.stdout.write(".")
	sys.stdout.flush()


class Command(BaseCommand):
	def __init__(self, *args, **kwargs):
		super(Command, self).__init__(*args, **kwargs)
		self.users_map = {}
		self.vocabulary_map = {}
		self.term_map = {}

	@cached_property
	def db_connection(self):
		return connections['blackhole']

	def db_cursor(self):
		return self.db_connection.cursor()

	@cached_property
	def filter_formats(self):
		with self.db_cursor() as cursor:
			cursor.execute('SELECT format, name FROM filter_formats')
			formats = tuple(FilterFormat(*row) for row in cursor.fetchall())
			return {f.format: FORMATS_TRANSLATION[f.name] for f in formats}

	@cached_property
	def vocabulary_node_types(self):
		with self.db_cursor() as cursor:
			cursor.execute('SELECT vid, type FROM vocabulary_node_types')
			return dict(cursor.fetchall())

	@property
	def nodes(self):
		with self.db_cursor() as cursor:
			cursor.execute('SELECT nid, type, title, uid, status, created, changed, comment, promote, sticky, vid FROM node')
			for row in cursor.fetchall():
				revisions = []
				terms = []
				with self.db_cursor() as revisions_cursor:
					revisions_cursor.execute('SELECT nid, vid, uid, title, body, teaser, timestamp, format, log FROM node_revisions WHERE nid = %s', [row[0]])
					for revision_row in revisions_cursor.fetchall():
						revisions.append(NodeRevisionData(*revision_row))
				with self.db_cursor() as terms_cursor:
					terms_cursor.execute('SELECT tid FROM term_node WHERE nid = %s', [row[0]])
					terms = [r[0] for r in terms_cursor.fetchall()]
				cols = list(row) + [revisions, terms]
				yield NodeData(*cols)

	def terms(self):
		with self.db_cursor() as cursor:
			cursor.execute('SELECT term_data.tid, term_hierarchy.parent, term_data.vid, term_data.name, description FROM term_data LEFT JOIN term_hierarchy ON term_data.tid = term_hierarchy.tid')
			return tuple(TermData(*row) for row in cursor.fetchall())

	def users(self):
		with self.db_cursor() as cursor:
			cursor.execute('SELECT uid, name, signature, created, login, status, picture FROM users')
			return tuple(UserData(*row) for row in cursor.fetchall())

	def files(self):
		with self.db_cursor() as cursor:
			cursor.execute('SELECT fid, nid, filename, filepath, filemime, filesize FROM files')
			return tuple(FileData(*row) for row in cursor.fetchall())

	def create_user(self, username, user_data):
		is_active = user_data.status == 1
		avatar = None
		if user_data.picture:
			avatar_filename = path.join(settings.MEDIA_ROOT, 'blackhole', user_data.picture)
			try:
				avatar = SimpleUploadedFile(path.basename(avatar_filename), open(avatar_filename, 'rb').read())
			except IOError:
				print('File does not exist: ' + avatar_filename)
		user = User(
			username=username,
			signature=user_data.signature,
			date_joined=timestamp_to_time(user_data.created),
			last_login=timestamp_to_time(user_data.login),
			is_active=is_active,
			avatar=avatar or '',
		)
		user.save()
		return user

	def sync_users(self):
		users_map = {}
		for user in self.users():
			dot()
			username = user.name
			user_instance = User.objects.filter(username=username).first()
			if user_instance is not None and user_instance.password == '':
				users_map[user.uid] = user_instance.pk
				continue
			if user_instance is None:
				user_instance = self.create_user(username, user)
			else:
				username = 'blackhole_' + username
				user_instance = User.objects.filter(username=username).first()
				if user_instance is None:
					user_instance = self.create_user(username, user)
			users_map[user.uid] = user_instance.pk
		return users_map

	def sync_vocabulary(self):
		vocabulary_map = {}
		for vid, fmt in self.vocabulary_node_types.items():
			dot()
			instance, _ = VocabularyNodeType.objects.get_or_create(name=fmt)
			vocabulary_map[vid] = instance.pk
		return vocabulary_map

	def sync_term(self):
		term_map = {}
		terms = {}

		def import_term(term_data, parent):
			dot()
			instance = (Term.objects
				.filter(parent=parent, vocabulary_id=term_data.vid, name=term_data.name)
				.first())
			if instance is None:
				instance = Term(
					parent=parent,
					vocabulary_id=term_data.vid,
					name=term_data.name,
					description=term_data.description
				)
				instance.save()
			term_map[term_data.tid] = instance
			if parent:
				parent = Term.objects.get(pk=parent.pk)
			for subterm in terms.get(term_data.tid, []):
				import_term(subterm, instance)

		for term in self.terms():
			terms.setdefault(term.parent, [])
			terms[term.parent].append(term)
		if not 0 in terms:
			return term_map

		for term in terms[0]:
			import_term(term, None)
		return term_map

	def sync_node(self):
		for node in self.nodes:
			dot()
			if Node.objects.filter(id=node.nid).exists():
				continue
			with transaction.atomic():
				node_instance = Node(
					id=node.nid,
					node_type=node.type,
					title=node.title,
					author_id=self.users_map.get(node.uid),
					is_published=int(node.status) == 1,
					is_commentable=int(node.comment) != 0,
					is_promoted=int(node.promote) == 1,
					is_sticky=int(node.sticky) == 1,
					revision_id=node.vid,
					created=timestamp_to_time(node.created),
					updated=timestamp_to_time(node.changed)
				)
				node_instance.save()
				for revision in node.revisions:
					body = revision.body
					revision_instance = NodeRevision(
						id=revision.vid,
						node=node_instance,
						title=revision.title,
						author_id=self.users_map.get(node.uid),
						original_body=(self.filter_formats.get(revision.format, 'raw') + ':' + body),
						log=revision.log or '',
						created=timestamp_to_time(revision.timestamp),
						updated=timestamp_to_time(revision.timestamp)
					)
					revision_instance.save()
				for term_id in node.terms:
					node_instance.terms.add(self.term_map[term_id])

	def sync_file(self):
		for file_data in self.files():
			dot()
			if File.objects.filter(id=file_data.fid).exists():
				continue
			file_instance = File(
				id=file_data.fid,
				node_id=file_data.nid,
				filename=file_data.filename,
				filepath=path.join('blackhole', file_data.filepath),
				filemime=file_data.filemime,
				filesize=file_data.filesize
			)
			file_instance.save()

	def handle(self, *args, **options):
		with transaction.atomic():
			print("Users")
			self.users_map = self.sync_users()
			print("")
			print("Vocabulary type")
			self.vocabulary_map = self.sync_vocabulary()
			print("")
			print("Term")
			self.term_map = self.sync_term()
			print("")
			print("Node")
			self.sync_node()
			print("")
			print("File")
			self.sync_file()
			print("")
