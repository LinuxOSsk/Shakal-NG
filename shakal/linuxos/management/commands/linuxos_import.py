# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import connections
from django.template.defaultfilters import slugify
from shakal.accounts.models import UserProfile
from shakal.article.models import Article, Category as ArticleCategory
import sys

class Command(BaseCommand):
	args = ''
	help = 'Import data from LinuxOS'

	def decode_cols_to_dict(self, names, values):
		return dict(zip(names, values))

	def empty_if_null(self, value):
		return self.get_default_if_null(value, '')

	def first_datetime_if_null(self, dt):
		return self.get_default_if_null(dt, datetime(1970, 1, 1))

	def get_default_if_null(self, value, default):
		if value is None:
			return default
		else:
			return value

	def handle(self, *args, **kwargs):
		self.cursor = connections["linuxos"].cursor()
		#self.import_users()
		self.import_articles()

	def import_users(self):
		cols = [
			'id',
			'jabber',
			'url',
			'signatura',
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
				'signature': self.empty_if_null(user_dict['signature']),
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
		connections['default'].cursor().execute('SELECT setval(\'auth_user_id_seq\', (SELECT MAX(id) FROM auth_user));')

	def import_articles(self):
		self.import_article_categories()
		self.import_article_contents()

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
		connections['default'].cursor().execute('SELECT setval(\'article_category_id_seq\', (SELECT MAX(id) FROM article_category));')

	def import_article_contents(self):
		cols = [
			'id',
			'kategoria',
			'nazov',
			'titulok',
			'anotacia',
			'clanok',
			'uid',
			'username',
			'time',
			'published',
			'mesiaca',
			'file',
			'zobrazeni'
		]
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM clanky')
		articles = []
		unique_slugs = {}
		for clanok_row in self.cursor:
			clanok_dict = self.decode_cols_to_dict(cols, clanok_row)
			slug = slugify(clanok_dict['nazov'])[:45]
			if slug in unique_slugs:
				unique_slugs[slug] += 1
				slug = slug + '-' + str(unique_slugs[slug])
			unique_slugs[slug] = 1
			clanok = {
				'pk': clanok_dict['id'],
				'title': clanok_dict['nazov'],
				'slug': slug,
				'category_id': 1 if clanok_dict['kategoria'] == 0 else clanok_dict['kategoria'],
				'perex': clanok_dict['titulok'],
				'annotation': clanok_dict['anotacia'],
				'content': clanok_dict['clanok'],
				'author_id': clanok_dict['uid'],
				'authors_name': clanok_dict['username'],
				'time': self.first_datetime_if_null(clanok_dict['time']),
				'published': True if clanok_dict['published'] == 'yes' else False,
				'top': True if clanok_dict['mesiaca'] == 'yes' else False,
				'image': clanok_dict['file'],
				'display_count': clanok_dict['zobrazeni'],
			}
			articles.append(Article(**clanok))
		Article.objects.bulk_create(articles)
