# -*- coding: utf-8 -*-
import subprocess
import sys
from collections import namedtuple
from datetime import datetime
from os import path

import pytz
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand
from django.db import transaction, connections
from django.utils.functional import cached_property

from ...models import Term, Node, NodeRevision, File
from accounts.models import User
from blackhole.models import VocabularyNodeType
from comments.models import Comment
from comments.utils import update_comments_header
from rich_editor.widgets import TextVal


#from common_utils.asciitable import NamedtupleTablePrinter


COMMENT_NODE_HIDDEN = 0
COMMENT_NODE_CLOSED = 1
COMMENT_NODE_OPEN = 2

NODE_NOT_PUBLISHED = 0
NODE_PUBLISHED = 1

NODE_NOT_PROMOTED = 0
NODE_PROMOTED = 1

NODE_NOT_STICKY = 0
NODE_STICKY = 1

USER_STATUS_BLOCKED = 0
USER_STATUS_ACTIVE = 1

BLACKHOLE_BODY_REPLACE = (
	('"/files/', '"/media/blackhole/files/'),
	('\'/files/', '\'/media/blackhole/files/'),
	('http://blackhole.sk/files/', '/media/blackhole/files/'),
	('https://blackhole.sk/files/', '/media/blackhole/files/'),
	('http://www.blackhole.sk/files/', '/media/blackhole/files/'),
	('https://www.blackhole.sk/files/', '/media/blackhole/files/'),
)


FilterFormat = namedtuple('FilterFormat', ['format', 'name'])
FormatInfo = namedtuple('FormatInfo', ['format', 'name', 'delta', 'module'])
NodeData = namedtuple('NodeData', ['nid', 'type', 'title', 'uid', 'status', 'created', 'changed', 'comment', 'promote', 'sticky', 'vid', 'revisions', 'terms'])
NodeRevisionData = namedtuple('NodeRevisionData', ['nid', 'vid', 'uid', 'title', 'body', 'teaser', 'timestamp', 'format', 'log'])
TermData = namedtuple('TermData', ['tid', 'parent', 'vid', 'name', 'description'])
UserData = namedtuple('UserData', ['uid', 'name', 'signature', 'created', 'login', 'status', 'picture'])
FileData = namedtuple('FileData', ['fid', 'nid', 'filename', 'filepath', 'filemime', 'filesize'])
CommentData = namedtuple('CommentData', ['cid', 'pid', 'nid', 'uid', 'subject', 'comment', 'timestamp', 'format', 'name'])


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
	def node_ctype(self):
		return ContentType.objects.get_for_model(Node)

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
	def formats_filtering(self):
		formats = {}
		with self.db_cursor() as cursor:
			cursor.execute('SELECT filter_formats.format, filter_formats.name, filters.delta, filters.module FROM filter_formats LEFT JOIN filters ON filters.format = filter_formats.format ORDER BY filters.weight ASC')
			format_rows = tuple(FormatInfo(*row) for row in cursor.fetchall())
			for row in format_rows:
				formats.setdefault(row.format, [])
				formats[row.format].append(row)
		return formats

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

	def comments(self):
		with self.db_cursor() as cursor:
			cursor.execute('SELECT cid, pid, nid, uid, subject, comment, timestamp, format, name FROM comments ORDER BY nid, cid')
			for row in cursor.fetchall():
				yield CommentData(*row)

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
			username=username[:30],
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
			username = user.name or 'blackhole'
			user_instance = User.objects.filter(username=username[:30]).first()
			if user_instance is not None and user_instance.password == '':
				users_map[user.uid] = user_instance.pk
				continue
			if user_instance is None:
				user_instance = self.create_user(username[:30], user)
			else:
				username = 'blackhole_' + username
				user_instance = User.objects.filter(username=username[:30]).first()
				if user_instance is None:
					user_instance = self.create_user(username[30], user)
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
				.filter(parent=parent, vocabulary_id=self.vocabulary_map[term_data.vid], name=term_data.name)
				.first())
			if instance is None:
				instance = Term(
					parent=parent,
					vocabulary_id=self.vocabulary_map[term_data.vid],
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

	def call_filters(self, body, filters):
		body = body.encode('utf-8')
		for drupal_filter in filters:
			filter_php = path.join(path.dirname(__file__), drupal_filter.module + '.php')
			body = subprocess.Popen(['php', filter_php, 'prepare', str(drupal_filter.delta), str(drupal_filter.format)], stdout=subprocess.PIPE, stdin=subprocess.PIPE).communicate(body)[0]
		for drupal_filter in filters:
			filter_php = path.join(path.dirname(__file__), drupal_filter.module + '.php')
			body = subprocess.Popen(['php', filter_php, 'process', str(drupal_filter.delta), str(drupal_filter.format)], stdout=subprocess.PIPE, stdin=subprocess.PIPE).communicate(body)[0]
		return body.decode('utf-8')

	def sync_node(self):
		for node in self.nodes:
			dot()
			if Node.objects.filter(id=node.nid).exists():
				root = Comment.objects.get_or_create_root_comment(self.node_ctype, node.nid)[0]
				if int(node.comment) == COMMENT_NODE_CLOSED:
					root.is_locked = True
					root.save()
				update_comments_header(Comment, instance=root)
				continue
			with transaction.atomic():
				node_instance = Node(
					id=node.nid,
					node_type=node.type,
					title=node.title,
					author_id=self.users_map.get(node.uid),
					is_published=int(node.status) == NODE_PUBLISHED,
					is_commentable=int(node.comment) != COMMENT_NODE_HIDDEN,
					is_promoted=int(node.promote) == NODE_PROMOTED,
					is_sticky=int(node.sticky) == NODE_STICKY,
					revision_id=node.vid,
					created=timestamp_to_time(node.created),
					updated=timestamp_to_time(node.changed)
				)
				node_instance.save()
				for revision in node.revisions:
					body = revision.body
					for search, replace in BLACKHOLE_BODY_REPLACE:
						body = body.replace(search, replace)
					filters = self.formats_filtering.get(revision.format, self.formats_filtering[1])
					filtered_body = self.call_filters(body, filters)
					revision_instance = NodeRevision(
						id=revision.vid,
						node=node_instance,
						title=revision.title,
						author_id=self.users_map.get(node.uid),
						original_body=TextVal(self.filter_formats.get(revision.format, 'raw') + ':' + body),
						log=revision.log or '',
						created=timestamp_to_time(revision.timestamp),
						updated=timestamp_to_time(revision.timestamp)
					)
					revision_instance.save()
					NodeRevision.objects.filter(pk=revision_instance.pk).update(filtered_body=filtered_body)
				for term_id in node.terms:
					node_instance.terms.add(self.term_map[term_id])
				root = Comment.objects.get_or_create_root_comment(self.node_ctype, node.nid)[0]
				if int(node.comment) == COMMENT_NODE_CLOSED:
					root.is_locked = True
					root.save()
				update_comments_header(Comment, instance=root)

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

	def sync_comment(self):
		comments_map = {}
		root_header = None
		root_comment = None

		for comment in self.comments():
			dot()
			if root_header is None or root_header.object_id != comment.nid:
				root_comment = Comment.objects.get_or_create_root_comment(self.node_ctype, comment.nid)[0]
			update_comments_header(Comment, instance=root_comment)
			filters = self.formats_filtering.get(comment.format, self.formats_filtering[1])
			filtered_comment = self.call_filters(comment.comment, filters)
			time_created = timestamp_to_time(comment.timestamp)
			comment_instance = Comment(
				parent_id=comments_map[comment.pid] if comment.pid else root_comment.id,
				object_id=comment.nid,
				content_type=self.node_ctype,
				subject=comment.subject,
				created=time_created,
				updated=time_created,
				user_id=self.users_map.get(comment.uid),
				user_name=comment.name,
				is_public=True,
				is_locked=root_comment.is_locked,
				original_comment=TextVal(self.filter_formats.get(comment.format, 'raw') + ':' + comment.comment),
			)
			comment_instance.save()
			Comment.objects.filter(pk=comment_instance.pk).update(filtered_comment=filtered_comment)
			comments_map[comment.cid] = comment_instance.pk

	def handle(self, *args, **options):
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
		print("Comment")
		self.sync_comment()
		print("")
