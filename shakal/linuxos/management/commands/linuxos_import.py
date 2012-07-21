# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import connections
from django.template.defaultfilters import slugify
from shakal.accounts.models import UserProfile
from shakal.article.models import Category as ArticleCategory
import sys

class Command(BaseCommand):
	args = ''
	help = 'Import data from LinuxOS'

	def decode_cols_to_dict(self, names, values):
		return dict(zip(names, values))

	def empty_if_null(slef, value):
		if value is None:
			return ""
		else:
			return value

	def first_datetime_if_null(self, dt):
		if dt is None:
			return datetime(1970, 1, 1)
		else:
			return dt

	def handle(self, *args, **kwargs):
		self.cursor = connections["linuxos"].cursor()
		self.import_users()
		self.import_articles()

	def import_users(self):
		cols = [
			'id',
			'jabber',
			'url',
			'nick',
			'heslo',
			'email',
			'zobrazit_mail',
			'prava',
			'lastlogin',
			'signatura',
			'more_info',
			'info',
			'rok',
			'real_name',
		]
		self.cursor.execute('SELECT COUNT(*) FROM users')
		count = self.cursor.fetchall()[0][0]
		counter = 0
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM users')
		for user in self.cursor:
			counter += 1
			sys.stdout.write("{0} / {1}\r".format(counter, count))
			sys.stdout.flush()
			user_dict = self.decode_cols_to_dict(cols, user)
			base_user = {
				'pk': user_dict['id'],
				'username': user_dict['nick'][:30],
				'email': user_dict['email'][:75],
				'password': user_dict['heslo'],
				'is_active': False,
				'last_login': self.first_datetime_if_null(user_dict['lastlogin']),
			}
			if user_dict['real_name']:
				space_pos = user_dict['real_name'].find(' ')
				if space_pos == -1:
					base_user['first_name'] = user_dict['real_name']
				else:
					base_user['first_name'] = user_dict['real_name'][:space_pos]
					base_user['last_name'] = user_dict['real_name'][space_pos + 1:]
			if user_dict['prava'] > 0:
				base_user['is_active'] = True
				if user_dict['prava'] > 1:
					base_user['is_staff'] = True
					if user_dict['prava'] > 2:
						base_user['is_superuser'] = True
			user_object = User(**base_user)
			user_object.set_password(base_user['password'])
			user_object.save()
			user_profile = {
				'jabber': self.empty_if_null(user_dict['jabber']),
				'url': self.empty_if_null(user_dict['url']),
				'display_mail': self.empty_if_null(user_dict['zobrazit_mail']),
				'distribution': self.empty_if_null(user_dict['more_info']),
				'info': self.empty_if_null(user_dict['info']),
				'year': user_dict['rok'],
				'user_id': user_dict['id'],
			}
			user_profile_object = UserProfile.objects.get(user_id = user_object.pk)
			for attribute in user_profile:
				setattr(user_profile_object, attribute, user_profile[attribute])
			user_profile_object.save()

	def import_articles(self):
		self.import_article_categories()

	def import_article_categories(self):
		cols = [
			'id',
			'nazov',
			'ikona',
		]
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM clanky_kategorie')
		for category_row in self.cursor:
			category_dict = self.decode_cols_to_dict(cols, category_row)
			category = {
				'pk': category_dict['id'],
				'name': category_dict['nazov'],
				'icon': category_dict['ikona'],
				'slug': slugify(category_dict['nazov']),
			}
			category_object = ArticleCategory(**category)
			category_object.save()
