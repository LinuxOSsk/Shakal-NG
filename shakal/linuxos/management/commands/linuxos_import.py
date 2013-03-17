# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime

import json
import reversion
import socket
import threading
import urllib
import urllib2
from collections import OrderedDict
from cookielib import CookieJar
from copy import copy
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.core.serializers.json import Deserializer
from django.db import connections, connection, models
from django.template.defaultfilters import slugify
from phpserialize import loads
from progressbar import Bar, BouncingBar, ETA, FormatLabel, ProgressBar, RotatingMarker
from subprocess import call, Popen, PIPE

from accounts.models import User
from polls.models import Poll, Choice as PollChoice
from hitcount.models import HitCount
from shakal.article.models import Article, Category as ArticleCategory
from shakal.forum.models import Section as ForumSection, Topic as ForumTopic
from shakal.news.models import News
from shakal.threaded_comments.models import RootHeader as ThreadedRootHeader, UserDiscussionAttribute
from shakal.utils import create_unique_slug
from shakal.wiki.models import Page as WikiPage


class SocketMaintenance(object):
	def __init__(self):
		self.address = os.path.abspath("maintenance.flag")
		try:
			os.unlink(self.address)
		except OSError:
			if os.path.exists(self.address):
				raise
		self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		self.sock.bind(self.address)
		self.sock.listen(1)
		self.thread = threading.Thread(target = self.process_connections)
		self.thread.start()

	def finish(self):
		self.sock.shutdown(2)
		self.thread.join()
		try:
			os.unlink(self.address)
		except OSError:
			if os.path.exists(self.address):
				raise

	def process_connections(self):
		while True:
			try:
				sock_connection, address = self.sock.accept()
			except:
				return
			try:
				sock_connection.sendall(self.get_info())
			finally:
				sock_connection.close()


class ProgressLogger(SocketMaintenance):
	def __init__(self):
		super(ProgressLogger, self).__init__()
		self.main_progress = {'text': '', 'steps': 0, 'progress': 0}
		self.sub_progress = {'text': '', 'steps': 0, 'progress': 0}
		self.pb_widgets = [FormatLabel('%(value)6d / %(max)-6d '), Bar('>'), ' ', ETA()]
		self.pb_widgets_bounce = [FormatLabel('%(value)6d (%(elapsed)s) '), BouncingBar(marker=RotatingMarker())]
		self.progressbar = None

	def set_main_progress(self, text, steps, progress = 0):
		if text != self.main_progress['text']:
			print("\x1b[37;1m" + text + '\x1b[0m')
		self.main_progress = {'text': text, 'steps': steps, 'progress': progress}

	def set_sub_progress(self, text, steps, progress = 0):
		if self.progressbar is None:
			if not steps:
				self.progressbar = ProgressBar(widgets = [text] + self.pb_widgets_bounce, maxval = steps)
			else:
				self.progressbar = ProgressBar(widgets = [text] + self.pb_widgets, maxval = steps)
			self.progressbar.start()
		if not steps:
			self.progressbar.widgets[0] = "%-15s " % text
		else:
			self.progressbar.widgets[0] = "%-16s " % text
		self.progressbar.update(progress)
		self.sub_progress = {'text': text, 'steps': steps, 'progress': progress}

	def step_main_progress(self, text = None):
		self.finish_sub_progress()
		p = copy(self.main_progress)
		p['progress'] += 1
		if text is not None:
			p['text'] = text
		self.set_main_progress(**p)

	def step_sub_progress(self, text = None):
		p = copy(self.sub_progress)
		p['progress'] += 1
		if text is not None:
			p['text'] = text
		self.set_sub_progress(**p)

	def finish_main_progress(self):
		self.finish_sub_progress()

	def finish_sub_progress(self):
		if self.progressbar is not None:
			self.progressbar.finish()
		self.progressbar = None

	def get_info(self):
		return json.dumps({"main_progress": self.main_progress, "sub_progress": self.sub_progress, "text": u"Import dát"})


class Command(BaseCommand):
	args = ''
	help = 'Import data from LinuxOS'

	def __init__(self, *args, **kwargs):
		self.logger = ProgressLogger()
		super(Command, self).__init__(*args, **kwargs)
		self.content_types = {
			'forum': ContentType.objects.get(app_label = 'forum', model = 'topic').pk,
			'clanky': ContentType.objects.get(app_label = 'article', model = 'article').pk,
			'spravy': ContentType.objects.get(app_label = 'news', model = 'news').pk,
			'anketa': ContentType.objects.get(app_label = 'polls', model = 'poll').pk,
		}
		self.inverted_content_types = dict([(v, k) for (k, v) in self.content_types.iteritems()])

	def __del__(self):
		self.logger.finish()

	def decode_cols_to_dict(self, names, values):
		return dict(zip([n.split('.')[-1] for n in names], values))

	def empty_if_null(self, value):
		return self.get_default_if_null(value, '')

	def first_datetime_if_null(self, dt):
		return self.get_default_if_null(dt, datetime(1970, 1, 1))

	def get_default_if_null(self, value, default):
		if value is None:
			return default
		else:
			return value

	def unescape(self, s):
		s = s.replace("&lt;", "<")
		s = s.replace("&gt;", ">")
		s = s.replace("&amp;", "&")
		return s

	def handle(self, *args, **kwargs):
		try:
			self.cursor = connections["linuxos"].cursor()
			self.logger.set_main_progress(u"Import LinuxOS", 11, 0)
			self.logger.step_main_progress(u"Čistenie databázy")
			self.clean_db()
			self.logger.step_main_progress(u"Sťahovanie starej databázy")
			#self.download_db()
			self.logger.step_main_progress(u"Import užívateľov")
			self.import_users()
			self.logger.step_main_progress(u"Import článkov")
			self.import_articles()
			self.logger.step_main_progress(u"Import fóra")
			self.import_forum()
			self.logger.step_main_progress(u"Import správ")
			self.import_news()
			self.logger.step_main_progress(u"Import ankiet")
			self.import_polls()
			self.logger.step_main_progress(u"Import diskusie")
			self.import_discussion()
			self.logger.step_main_progress(u"Import atribútov diskusie")
			self.import_discussion_attributes()
			self.logger.step_main_progress(u"Import databázy znalostí")
			self.import_wiki()
			self.logger.finish_main_progress()
			self.finish_import()
		finally:
			self.logger.finish()

	def clean_db(self):
		tables = [
			('admin_tools_dashboard_preferences', ),
			('accounts_userrating', 'accounts_userrating_id_seq'),
			('wiki_page', 'wiki_page_id_seq'),
			('auth_group_permissions', 'auth_group_permissions_id_seq'),
			('auth_user_user_permissions', 'auth_user_user_permissions_id_seq'),
			('auth_group', 'auth_group_id_seq'),
			('threaded_comments_rootheader', 'threaded_comments_rootheader_id_seq'),
			('threaded_comments_userdiscussionattribute', 'threaded_comments_userdiscussionattribute_id_seq'),
			('django_comments', 'django_comments_id_seq'),
			('forum_topic', 'forum_topic_id_seq'),
			('django_admin_log', 'django_admin_log_id_seq'),
			('attachment_attachment', 'attachment_attachment_id_seq'),
			('attachment_temporaryattachment', 'attachment_temporaryattachment_id_seq'),
			('attachment_uploadsession', 'attachment_uploadsession_id_seq'),
			('article_category', 'article_category_id_seq'),
			('article_article', 'article_article_id_seq'),
			('news_news', 'news_news_id_seq'),
			('registration_registrationprofile', 'registration_registrationprofile_id_seq'),
			('polls_choice', 'polls_choice_id_seq'),
			('polls_recordip', 'polls_recordip_id_seq'),
			('polls_recorduser', 'polls_recorduser_id_seq'),
			('polls_poll', 'polls_poll_id_seq'),
			('forum_section', 'forum_section_id_seq'),
			('hitcount_hitcount', 'hitcount_hitcount_id_seq'),
			('auth_remember_remembertoken', ),
			('reversion_version', 'reversion_version_id_seq'),
			('reversion_revision', 'reversion_revision_id_seq'),
			('accounts_user', 'accounts_user_id_seq'),
		]

		self.logger.set_sub_progress(u"Tabuľka", len(tables))
		connections['default'].cursor().execute('SET CONSTRAINTS ALL DEFERRED')
		for table in tables:
			self.logger.step_sub_progress(u"%35s" % (table[0], ))
			connections['default'].cursor().execute('DELETE FROM ' + table[0] + '')
			if len(table) > 1:
				connections['default'].cursor().execute('SELECT setval(\'' + table[1] + '\', 1)')
		connections['default'].cursor().execute('SET CONSTRAINTS ALL IMMEDIATE')
		self.logger.finish_sub_progress()

	def download_db(self):
		cj = CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
		formdata = {
			'driver': 'server',
			'server': settings.DATABASES['linuxos_remote']['HOST'],
			'username': settings.DATABASES['linuxos_remote']['USER'],
			'password': settings.DATABASES['linuxos_remote']['PASSWORD']
		}
		data_encoded = urllib.urlencode(formdata)
		response = opener.open('https://cloud.relbit.com/tools/adminer/', data_encoded)
		response.read()
		formdata = {
			'output': 'gz',
			'format': 'sql',
			'db_style': '',
			'routines': '1',
			'events': '1',
			'table_style': 'DROP+CREATE',
			'auto_increment': '1',
			'triggers': '1',
			'data_style': 'INSERT',
			'databases[]': settings.DATABASES['linuxos_remote']['NAME']
		}
		data_encoded = urllib.urlencode(formdata)
		response = opener.open('https://cloud.relbit.com/tools/adminer/?server=' + settings.DATABASES['linuxos_remote']['HOST'] + '&username=' + settings.DATABASES['linuxos_remote']['USER'] + '&dump', data_encoded)
		f = open("dump.gz", "w")
		while True:
			content = response.read(1024 * 1024)
			if not content:
				break
			f.write(content)
			sys.stdout.write("\r" + str(f.tell() / (1024 * 1024)) + " MB")
			sys.stdout.flush()
		f.close()
		linuxos_settings = settings.DATABASES['linuxos']
		call('zcat dump.gz > dump.sql', shell = True)

		proc = Popen([
			'/usr/bin/mysql',
			'--user=' + linuxos_settings['USER'],
			'--password=' + linuxos_settings['PASSWORD'],
			'--host=' + linuxos_settings['HOST'],
			'--port=' + linuxos_settings['PORT'],
			linuxos_settings['NAME'],
		], stdin = PIPE)
		f = open("dump.sql", "r")
		progress = ProgressBar(widgets = ["Importing database", Bar('>'), ETA()], maxval = os.path.getsize("dump.sql"))
		progress.start()
		pos = 0L
		while True:
			progress.update(pos)
			content = f.read(1024 * 16)
			if not content:
				break
			pos += len(content)
			proc.stdin.write(content)
		progress.finish()
		proc.stdin.close()
		f.close()
		del proc
		call('cat dump.sql|mysql \
			--user=' + linuxos_settings['USER'] + ' \
			--password=' + linuxos_settings['PASSWORD'] + ' \
			--host=' + linuxos_settings['HOST'] + ' \
			--port=' + linuxos_settings['PORT'] + ' \
			' + linuxos_settings['NAME'], shell = True)
		php_filename = os.path.join(os.path.dirname(__file__), 'decrypt.php')
		call([
			'php', php_filename,
			linuxos_settings['USER'],
			linuxos_settings['PASSWORD'],
			linuxos_settings['HOST'],
			linuxos_settings['PORT'],
			linuxos_settings['NAME'],
			linuxos_settings['PRIV_KEY']])

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
			'more_info',
			'info',
			'rok',
			'real_name',
		]
		self.cursor.execute('SELECT COUNT(*) FROM users WHERE prava > 0')
		self.logger.set_sub_progress(u"Užívatelia", self.cursor.fetchall()[0][0])
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM users WHERE prava > 0')
		user_objects = []
		for user in self.cursor:
			self.logger.step_sub_progress()
			user_dict = self.decode_cols_to_dict(cols, user)
			user = {
				'pk': user_dict['id'],
				'username': user_dict['nick'][:30],
				'email': user_dict['email'][:75],
				'password': user_dict['heslo'],
				'is_active': False,
				'last_login': self.first_datetime_if_null(user_dict['lastlogin']),
				'jabber': self.empty_if_null(user_dict['jabber']),
				'url': self.empty_if_null(user_dict['url']),
				'signature': self.empty_if_null(user_dict['signatura']),
				'display_mail': self.empty_if_null(user_dict['zobrazit_mail']),
				'distribution': self.empty_if_null(user_dict['more_info']),
				'info': self.empty_if_null(user_dict['info']),
				'year': user_dict['rok'],
			}
			if user_dict['real_name']:
				space_pos = user_dict['real_name'].find(' ')
				if space_pos == -1:
					user['first_name'] = user_dict['real_name']
				else:
					user['first_name'] = user_dict['real_name'][:space_pos]
					user['last_name'] = user_dict['real_name'][space_pos + 1:]
			if user_dict['prava'] > 0:
				user['is_active'] = True
				if user_dict['prava'] > 1:
					user['is_staff'] = True
					if user_dict['prava'] > 2:
						user['is_superuser'] = True
			user_object = User(**user)
			user_object.set_password(user['password'])
			user_objects.append(user_object)
		User.objects.bulk_create(user_objects)
		connections['default'].cursor().execute('SELECT setval(\'accounts_user_id_seq\', (SELECT MAX(id) FROM accounts_user) + 1);')
		self.logger.finish_sub_progress()

	def import_articles(self):
		self.cursor.execute('SELECT COUNT(*) FROM clanky')
		self.articles_count = self.cursor.fetchall()[0][0]

		self.logger.set_sub_progress(u"Kategórie", None)
		self.import_article_categories()
		self.logger.finish_sub_progress()

		self.logger.set_sub_progress(u"Obsah", self.articles_count)
		self.import_article_contents()
		self.logger.finish_sub_progress()

		self.logger.set_sub_progress(u"Hlasovanie", self.articles_count)
		self.import_article_hitcount()
		self.logger.finish_sub_progress()

		self.import_article_images()

	def import_article_categories(self):
		cols = [
			'id',
			'nazov',
			'ikona',
		]
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM clanky_kategorie')
		for category_row in self.cursor:
			self.logger.step_sub_progress()
			category_dict = self.decode_cols_to_dict(cols, category_row)
			category = {
				'pk': category_dict['id'],
				'name': category_dict['nazov'],
				'icon': category_dict['ikona'],
				'slug': slugify(category_dict['nazov']),
			}
			category_object = ArticleCategory(**category)
			category_object.save()
		connections['default'].cursor().execute('SELECT setval(\'article_category_id_seq\', (SELECT MAX(id) FROM article_category) + 1);')

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
		]
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM clanky')
		articles = []
		unique_slugs = {}
		for clanok_row in self.cursor:
			self.logger.step_sub_progress()
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
				'pub_time': self.first_datetime_if_null(clanok_dict['time']),
				'updated': self.first_datetime_if_null(clanok_dict['time']),
				'published': True if clanok_dict['published'] == 'yes' else False,
				'top': True if clanok_dict['mesiaca'] == 'yes' else False,
				'image': clanok_dict['file'],
			}
			articles.append(Article(**clanok))
		Article.objects.bulk_create(articles)
		connections['default'].cursor().execute('SELECT setval(\'article_article_id_seq\', (SELECT MAX(id) FROM article_article) + 1);')

	def import_article_hitcount(self):
		cols = [
			'id',
			'zobrazeni',
		]
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM clanky')
		hitcount_map = {}
		for article in self.cursor:
			article_dict = self.decode_cols_to_dict(cols, article)
			hitcount_map[article_dict['id']] = article_dict['zobrazeni']

		hitcount = []
		for article in Article.objects.all():
			self.logger.step_sub_progress()
			hitcount.append(HitCount(content_object = article, hits = hitcount_map.get(article.pk, 0)))
		HitCount.objects.bulk_create(hitcount)

	def import_article_images(self):
		articles = Article.objects.exclude(image = '')[:]
		self.logger.set_sub_progress(u"Obrázky", len(articles))
		for article in articles:
			self.logger.step_sub_progress()
			image_file = str(article.image)
			if image_file[0] == '/':
				image_file = 'http://www.linuxos.sk' + image_file

			extension = os.path.splitext(image_file)[1]
			localpath = os.path.join('article', 'thumbnails', '{0:02x}'.format(article.pk % 256), str(article.pk), 'image_' + str(article.pk) + extension)
			dest = os.path.join(settings.MEDIA_ROOT, localpath)
			dest_dir = os.path.dirname(dest)
			if not os.path.exists(dest_dir):
				os.makedirs(dest_dir)
			try:
				urllib.urlretrieve(image_file, dest)
				article.image = localpath
				article.save()
			except IOError:
				pass
		self.logger.finish_sub_progress()

	def import_forum(self):
		self.import_forum_sections()
		self.import_forum_topics()

	def import_forum_sections(self):
		cols = [
			'id',
			'nazov',
			'popis'
		]
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM forum_sekcie')
		for section_row in self.cursor:
			section_dict = self.decode_cols_to_dict(cols, section_row)
			section_dict['nazov'] = self.unescape(section_dict['nazov'])
			section = {
				'pk': section_dict['id'],
				'name': section_dict['nazov'],
				'slug': slugify(section_dict['nazov']),
				'description': section_dict['popis'],
			}
			ForumSection(**section).save()
		connections['default'].cursor().execute('SELECT setval(\'forum_section_id_seq\', (SELECT MAX(id) FROM forum_section) + 1);')

	def import_forum_topics(self):
		users = set(map(lambda x: x['id'], User.objects.values('id')))
		cols = [
			'forum.id',
			'sekcia',
			'username',
			'predmet',
			'text',
			'userid',
			'datetime',
			'vyriesene',
		]
		self.cursor.execute('SELECT COUNT(*) FROM forum')
		self.logger.set_sub_progress(u"Fórum", self.cursor.fetchall()[0][0])
		counter = 0
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM forum LEFT JOIN diskusia_header ON forum.id = diskusia_header.diskusia_id AND kategoria = "forum" GROUP BY forum.id')
		topics = []
		for topic_row in self.cursor:
			self.logger.step_sub_progress()
			counter += 1
			topic_dict = self.decode_cols_to_dict(cols, topic_row)
			topic = {
				'pk': topic_dict['id'],
				'section_id': topic_dict['sekcia'],
				'authors_name': topic_dict['username'],
				'title': topic_dict['predmet'],
				'text': topic_dict['text'],
				'created': topic_dict['datetime'],
				'updated': topic_dict['datetime'],
				'is_resolved': self.get_default_if_null(topic_dict['vyriesene'], False),
			}
			if topic_dict['userid'] and topic_dict['userid'] in users:
				topic['author_id'] = topic_dict['userid']
			topics.append(ForumTopic(**topic))
			if counter % 1000 == 0:
				ForumTopic.objects.bulk_create(topics)
				topics = []
		ForumTopic.objects.bulk_create(topics)
		topics = []
		connections['default'].cursor().execute('SELECT setval(\'forum_topic_id_seq\', (SELECT MAX(id) FROM forum_topic) + 1);')
		self.logger.finish_sub_progress()

	def import_news(self):
		users = dict(map(lambda x: (x['id'], (x['first_name'], x['last_name'], x['username'])), User.objects.values('id', 'first_name', 'last_name', 'username')))
		all_slugs = set()
		cols = [
			'id',
			'predmet',
			'sprava',
			'userid',
			'time',
			'schvalene'
		]
		self.cursor.execute('SELECT COUNT(*) FROM spravy')
		self.logger.set_sub_progress(u"Správy", self.cursor.fetchall()[0][0])
		counter = 0
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM spravy')
		news_objects = []
		for news_row in self.cursor:
			self.logger.step_sub_progress()
			counter += 1
			news_dict = self.decode_cols_to_dict(cols, news_row)

			slug = str(news_dict['id'])
			if news_dict['predmet']:
				slug = create_unique_slug(slugify(news_dict['predmet'])[:45], all_slugs, 9999)
				all_slugs.add(slug)

			news = {
				'pk': news_dict['id'],
				'title': news_dict['predmet'] if news_dict['predmet'] else '-',
				'slug': slug,
				'short_text': news_dict['sprava'],
				'long_text': news_dict['sprava'],
				'created': news_dict['time'],
				'updated': news_dict['time'],
				'authors_name': '-',
				'approved': bool(news_dict['schvalene']),
			}
			if news_dict['userid'] in users:
				news['author_id'] = news_dict['userid']
				user = users[news_dict['userid']]
				if user[0] or user[1]:
					news['authors_name'] = (user[0] + ' ' + user[1]).strip()
				else:
					news['authors_name'] = user[2]
			news_objects.append(News(**news))
			if counter % 1000 == 0:
				News.objects.bulk_create(news_objects)
				news_objects = []
		News.objects.bulk_create(news_objects)
		news_objects = []
		connections['default'].cursor().execute('SELECT setval(\'news_news_id_seq\', (SELECT MAX(id) FROM news_news) + 1);')
		self.logger.finish_sub_progress()

	def import_polls(self):
		all_slugs = set()
		cols = [
			'id',
			'enabled',
			'checkbox',
			'od',
			'otazka',
			'odpovede',
			'hlasovanie',
			'schvalena',
			'article_id',
		]
		self.cursor.execute('SELECT COUNT(*) FROM anketa')
		self.logger.set_sub_progress(u"Anketa", self.cursor.fetchall()[0][0])
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM anketa')
		pollss = []
		for polls_row in self.cursor:
			polls_dict = self.decode_cols_to_dict(cols, polls_row)

			if polls_dict['article_id']:
				slug = 'article-' + str(polls_dict['article_id'])
				content_type = ContentType.objects.get_for_model(Article)
				object_id = polls_dict['article_id']
			else:
				slug = create_unique_slug(slugify(polls_dict['otazka'][:45]), all_slugs, 9999)
				content_type = None
				object_id = None
			all_slugs.add(slug)

			polls = {
				'pk': polls_dict['id'],
				'question': polls_dict['otazka'],
				'slug': slug,
				'checkbox': bool(polls_dict['checkbox']),
				'approved': bool(polls_dict['enabled']) and polls_dict['schvalena'] == 'yes',
				'active_from': polls_dict['od'],
				'answer_count': sum(int(x) if x else 0 for x in polls_dict['hlasovanie'].split('/')) if polls_dict['hlasovanie'] else 0,
				'content_type': content_type,
				'object_id': object_id,
			}
			pollss.append(Poll(**polls))
		pollss = dict([(polls.pk, polls) for polls in Poll.objects.bulk_create(pollss)])

		answers = []
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM anketa')
		for polls_row in self.cursor:
			self.logger.step_sub_progress()
			polls_dict = self.decode_cols_to_dict(cols, polls_row)
			polls_choices = loads(bytes(polls_dict['odpovede'].encode('utf-8')), array_hook=OrderedDict)
			polls_choices = [unicode(a[1], encoding='utf-8') for a in polls_choices.iteritems()]
			polls_votes = [int(x) if x else 0 for x in polls_dict['hlasovanie'].split('/')] if polls_dict['hlasovanie'] else []
			while (len(polls_votes) < len(polls_choices)):
				polls_votes.append(0)
			items = zip(polls_choices, polls_votes)
			for item in items:
				answers.append(PollChoice(polls = pollss[polls_dict['id']], answer = item[0], votes = item[1]))
		PollChoice.objects.bulk_create(answers)
		connections['default'].cursor().execute('SELECT setval(\'polls_poll_id_seq\', (SELECT MAX(id) FROM polls_poll) + 1);')
		connections['default'].cursor().execute('SELECT setval(\'polls_choice_id_seq\', (SELECT MAX(id) FROM polls_choice) + 1);')
		self.logger.finish_sub_progress()

	def import_discussion(self):
		self.import_discussion_headers()
		self.import_discussion_comments()

	def import_discussion_headers(self):
		cols = [
			'id',
			'diskusia_id',
			'kategoria',
			'time',
			'last_time',
			'reakcii',
			'zamknute',
			'vyriesene',
		]
		self.cursor.execute('SELECT COUNT(*) FROM diskusia_header')
		self.logger.set_sub_progress(u"Diskusia meta", self.cursor.fetchall()[0][0])
		counter = 0
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM diskusia_header')
		root_header_objects = []
		unique_check = set()
		for header_row in self.cursor:
			self.logger.step_sub_progress()
			counter += 1

			header_dict = self.decode_cols_to_dict(cols, header_row)
			if header_dict['kategoria'] == 'eshop':
				continue

			if (self.content_types[header_dict['kategoria']], header_dict['diskusia_id']) in unique_check:
				continue
			unique_check.add((self.content_types[header_dict['kategoria']], header_dict['diskusia_id']))

			header = {
				'id': header_dict['id'],
				'pub_date': header_dict['time'],
				'last_comment': header_dict['last_time'],
				'comment_count': self.get_default_if_null(header_dict['reakcii'], 0),
				'is_locked': bool(header_dict['zamknute']),
				'content_type_id': self.content_types[header_dict['kategoria']],
				'object_id': header_dict['diskusia_id'],
			}
			root_header_objects.append(ThreadedRootHeader(**header))
			if counter % 1000 == 0:
				ThreadedRootHeader.objects.bulk_create(root_header_objects)
				root_header_objects = []
		ThreadedRootHeader.objects.bulk_create(root_header_objects)
		root_header_objects = []
		connections['default'].cursor().execute('SELECT setval(\'threaded_comments_rootheader_id_seq\', (SELECT MAX(id) FROM threaded_comments_rootheader) + 1);')
		connections['default'].cursor().execute('\
			UPDATE forum_topic SET is_removed = true\
				WHERE forum_topic.id NOT IN\
					(SELECT object_id FROM threaded_comments_rootheader WHERE content_type_id = ' + str(self.content_types['forum']) + ')\
		')
		connections['default'].cursor().execute('UPDATE threaded_comments_rootheader SET last_comment = (SELECT created FROM forum_topic WHERE id = object_id) WHERE last_comment IS NULL AND content_type_id = ' + str(self.content_types['forum']) + ';')
		self.logger.finish_sub_progress()

	def decode_username_for_comment(self, comment_row):
		if (comment_row['first_name'] + ' ' + comment_row['last_name']).strip():
			comment_row['fullname'] = (comment_row['first_name'] + ' ' + comment_row['last_name']).strip()
		else:
			comment_row['fullname'] = comment_row['username']

		del comment_row['first_name']
		del comment_row['last_name']
		del comment_row['username']
		return comment_row

	def import_discussion_comments(self):
		users = set(map(lambda x: x['id'], User.objects.values('id')))
		cols = [
			'id',
			'parent',
			'username',
			'userid',
			'predmet',
			'text',
			'time',
			'locked',
		]
		insert_cols = [
			'id',
			'content_type_id',
			'object_pk',
			'site_id',
			'subject',
			'parent_id',
			'user_id',
			'user_name',
			'user_email',
			'user_url',
			'comment',
			'submit_date',
			'ip_address',
			'is_public',
			'is_removed',
			'is_locked',
			'updated',
			'lft',
			'rght',
			'tree_id',
			'level',
		]
		insert_query = 'INSERT INTO django_comments (' + (','.join(insert_cols)) + ') VALUES (' + (("%s, " * len(insert_cols))[:-2]) + ')'
		select_query = 'SELECT ' + (', '.join(['diskusia.' + col for col in cols])) + ', diskusia_header.diskusia_id FROM diskusia INNER JOIN diskusia_header ON (diskusia.diskusiaid = diskusia_header.id) WHERE diskusia_id = {0} AND kategoria = "{1}" ORDER BY diskusia.id'
		headers = ThreadedRootHeader.objects.values_list('id', 'content_type_id', 'object_id', 'is_locked', 'pub_date')
		counter = 0
		comment_counter = 0
		self.logger.set_sub_progress(u"Diskusia obsah", len(headers))

		comments = []

		for id, content_type_id, object_pk, is_locked, pub_date in headers:
			self.logger.step_sub_progress()
			counter += 1
			comment_counter += 1
			comment_tree = {}
			comments.append({
				'id': comment_counter,
				'content_type_id': content_type_id,
				'object_pk': object_pk,
				'site_id': settings.SITE_ID,
				'subject': '',
				'parent_id': None,
				'user_id': None,
				'user_name': '',
				'user_email': '',
				'user_url': '',
				'comment': '',
				'submit_date': pub_date,
				'ip_address': None,
				'is_public': True,
				'is_removed': False,
				'is_locked': is_locked,
				'updated': pub_date,
				'lft': 0,
				'rght': 0,
				'tree_id': counter,
				'level': 0,
			})
			comment_tree[0] = [comments[-1]]
			root_comment_id = comment_counter
			self.cursor.execute(select_query.format(object_pk, self.inverted_content_types[content_type_id]))
			comment_rows = [self.decode_cols_to_dict(cols, r) for r in list(self.cursor)]
			for comment_dict in comment_rows:
				comment_counter += 1
				comment_dict['pk'] = comment_counter
			pk_map = dict((d['id'], d['pk']) for d in comment_rows)
			for comment_dict in comment_rows:
				try:
					parent = pk_map[comment_dict['parent']]
				except KeyError:
					parent = root_comment_id
				if comment_dict['userid'] and comment_dict['userid'] in users:
					user_id = comment_dict['userid']
				else:
					user_id = None
				comment = {
					'id': comment_dict['pk'],
					'content_type_id': content_type_id,
					'object_pk': object_pk,
					'site_id': settings.SITE_ID,
					'subject': comment_dict['predmet'],
					'parent_id': parent,
					'user_id': user_id,
					'user_name': comment_dict['username'],
					'user_email': '',
					'user_url': '',
					'comment': comment_dict['text'],
					'submit_date': comment_dict['time'],
					'ip_address': None,
					'is_public': True,
					'is_removed': False,
					'is_locked': is_locked or (True if comment_dict['locked'] == 'yes' else False),
					'updated': comment_dict['time'],
					'lft': 0,
					'rght': 0,
					'tree_id': counter,
					'level': 0,
				}
				comments.append(comment)
				if not comment['parent_id'] in comment_tree:
					comment_tree[comment['parent_id']] = []
				comment_tree[comment['parent_id']].append(comment)
			self.lr_counter = 0
			self.depth = -1
			self.make_tree_structure(comment_tree, 0)
			if counter % 1000 == 0:
				comments_data = map(lambda c: tuple([c[col] for col in insert_cols]), comments)
				connection.cursor().executemany(insert_query, comments_data)
				comments = []
		comments_data = map(lambda c: tuple([c[col] for col in insert_cols]), comments)
		connection.cursor().executemany(insert_query, comments_data)
		comments = []

		connections['default'].cursor().execute('SELECT setval(\'threaded_comments_rootheader_id_seq\', (SELECT MAX(id) FROM threaded_comments_rootheader) + 1);')
		connections['default'].cursor().execute('SELECT setval(\'django_comments_id_seq\', (SELECT MAX(id) FROM django_comments) + 1);')
		self.logger.finish_sub_progress()

	def import_discussion_attributes(self):
		root_headers = set(ThreadedRootHeader.objects.values_list('id', flat = True))
		users = set(User.objects.values_list('id', flat = True))

		self.cursor.execute('SELECT userid, diskusiaid, time FROM diskusia_zvyraznenie')
		time = self.cursor.fetchall()
		data = dict(map(lambda x: ((x[0], x[1]), {'user_id': x[0], 'discussion_id': x[1], 'time': x[2], 'watch': False}), time))

		self.cursor.execute('SELECT uid, diskusia_id FROM diskusia_watch')
		watch = self.cursor.fetchall()
		for item in watch:
			key = (item[0], item[1])
			if key in data:
				data[key]['watch'] = True
			else:
				data[key] = {'user_id': item[0], 'discussion_id': item[1], 'time': None, 'watch': True}

		self.logger.set_sub_progress(u"Atribúty diskusie", len(data))
		metadata = []
		counter = 0
		for (key, value) in data.iteritems():
			self.logger.step_sub_progress()
			counter += 1
			if counter % 1000 == 0:
				UserDiscussionAttribute.objects.bulk_create(metadata)
				metadata = []
			if value['discussion_id'] in root_headers and value['user_id'] in users:
				metadata.append(UserDiscussionAttribute(**value))
		UserDiscussionAttribute.objects.bulk_create(metadata)
		metadata = []
		connections['default'].cursor().execute('SELECT setval(\'threaded_comments_userdiscussionattribute_id_seq\', (SELECT MAX(id) FROM threaded_comments_userdiscussionattribute) + 1);')
		self.logger.finish_sub_progress()

	def import_wiki(self):
		models.signals.pre_save.disconnect(dispatch_uid='setup_index_signals')
		models.signals.post_save.disconnect(dispatch_uid='setup_index_signals')
		users = set(User.objects.values_list('id', flat = True))
		all_slugs = set()
		categories = {}
		for instance in Deserializer(open('shakal/wiki/pages.json')):
			instance.object.created = datetime.now()
			instance.object.save()
			categories[instance.object.title.replace('&amp;', '&')] = instance.object.id
			all_slugs.add(instance.object.slug)

		cols = [
			'id',
			'nadpis',
			'text',
			'time',
			'userid',
			'kategoria',
			'nazov_kategorie',
		]
		select_query = 'SELECT ' + (', '.join(['KnowledgeBase.' + col for col in cols])) + ' FROM KnowledgeBase ORDER BY KnowledgeBase.id DESC'
		self.cursor.execute(select_query)
		wiki_pages = [self.decode_cols_to_dict(cols, r) for r in list(self.cursor)]
		wiki_pages = dict([(p['id'], [p]) for p in wiki_pages])

		select_query = 'SELECT ' + (', '.join(['KnowledgeBase_History.' + col for col in cols])) + ' FROM KnowledgeBase_History ORDER BY KnowledgeBase_History.id'
		self.cursor.execute(select_query)
		wiki_history = [self.decode_cols_to_dict(cols, r) for r in list(self.cursor)]
		for item in wiki_history:
			if item['id'] in wiki_pages:
				wiki_pages[item['id']].insert(0, item)

		count = 0
		for id, page_list in wiki_pages.iteritems():
			count += len(page_list)

		reversion.register(WikiPage)

		self.logger.set_sub_progress(u"Databáza znalostí", count)
		for id, page_list in wiki_pages.iteritems():
			page_object = None
			for page in page_list:
				page['nadpis'] = page['nadpis'].replace('&amp;', '&')
				page['nazov_kategorie'] = page['nazov_kategorie'].replace('&amp;', '&')
				if not page_object:
					page_object = WikiPage()

				user = None
				if page['userid'] in users:
					page_object.last_author_id = page['userid']
					user = User.objects.get(pk = page['userid'])
				page_object.id = page['id'] + 7
				page_object.title = page['nadpis']
				page_object.text = page['text']
				page_object.updated = page['time']
				page_object.parent = WikiPage.objects.get(pk = categories[page['nazov_kategorie']])
				page_object.page_type = 'p'
				if not page_object.created:
					page_object.created = page['time']
				if not page_object.slug:
					slug = create_unique_slug(slugify(page['nadpis'])[:45], all_slugs, 9999)
					all_slugs.add(slug)
					page_object.slug = slug
				page_object.save(ignore_auto_date = True)
				revision = reversion.revision.save_revision([page_object], user = user)
				revision.date_created = page['time']
				revision.save()

				self.logger.step_sub_progress()
		self.logger.finish_sub_progress()

		connections['default'].cursor().execute('SELECT setval(\'wiki_page_id_seq\', (SELECT MAX(id) FROM wiki_page) + 1);')

	def make_tree_structure(self, tree_items, root):
		items = tree_items[root]
		self.depth += 1
		for item in items:
			self.lr_counter += 1
			item['lft'] = self.lr_counter
			if not item['lft']:
				print(item['lft'])
			item['level'] = self.depth
			if item['id'] in tree_items:
				self.make_tree_structure(tree_items, item['id'])
			self.lr_counter += 1
			item['rght'] = self.lr_counter
		self.depth -= 1

	def finish_import(self):
		connections['default'].cursor().execute('COMMIT;')
