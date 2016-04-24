# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
from os import path
from collections import namedtuple
from datetime import datetime
from django.core.files.uploadedfile import SimpleUploadedFile

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connections
from django.utils.functional import cached_property
import pytz

from accounts.models import User


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
NodeData = namedtuple('NodeData', ['nid', 'type', 'title', 'uid', 'status', 'created', 'changed', 'comment', 'promote', 'sticky', 'vid'])
TermData = namedtuple('TermData', ['tid', 'parent', 'vid', 'name', 'description'])
UserData = namedtuple('UserData', ['uid', 'name', 'signature', 'created', 'login', 'status', 'picture'])


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

	@cached_property
	def db_connection(self):
		return connections['blackhole']

	def db_cursor(self):
		return self.db_connection.cursor()

	@cached_property
	def filter_formats(self):
		cursor = self.db_cursor()
		cursor.execute('SELECT format, name FROM filter_formats')
		formats = tuple(FilterFormat(*row) for row in cursor.fetchall())
		return {f.format: FORMATS_TRANSLATION[f.name] for f in formats}

	def nodes(self):
		cursor = self.db_cursor()
		cursor.execute('SELECT nid, type, title, uid, status, created, changed, comment, promote, sticky, vid FROM node')
		nodes = tuple(NodeData(row) for row in cursor.fetchall())
		for node in nodes:
			yield node

	def terms(self):
		cursor = self.db_cursor()
		cursor.execute('SELECT term_data.tid, term_hierarchy.parent, term_data.vid, term_data.name, description FROM term_data LEFT JOIN term_hierarchy ON term_data.tid = term_hierarchy.tid')
		return tuple(TermData(*row) for row in cursor.fetchall())

	def users(self):
		cursor = self.db_cursor()
		cursor.execute('SELECT uid, name, signature, created, login, status, picture FROM users')
		return tuple(UserData(*row) for row in cursor.fetchall())

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

	def handle(self, *args, **options):
		print("Users")
		self.users_map = self.sync_users()
		print("")
