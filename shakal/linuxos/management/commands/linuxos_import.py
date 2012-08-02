# -*- coding: utf-8 -*-

from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from django.core.management.base import BaseCommand
from django.db import connections
from django.template.defaultfilters import slugify
from shakal.accounts.models import UserProfile
from shakal.article.models import Article, Category as ArticleCategory
from shakal.forum.models import Section as ForumSection, Topic as ForumTopic
from shakal.news.models import News
from shakal.survey.models import Survey, Answer as SurveyAnswer
from shakal.threaded_comments.models import ThreadedComment, RootHeader as ThreadedRootHeader
from shakal.utils import create_unique_slug
from hitcount.models import HitCount
from collections import OrderedDict
import os
import sys
import urllib
from phpserialize import loads

class Command(BaseCommand):
	args = ''
	help = 'Import data from LinuxOS'

	def __init__(self, *args, **kwargs):
		super(Command, self).__init__(*args, **kwargs)
		self.content_types = {
			'forum': ContentType.objects.get(app_label = 'forum', model = 'topic').pk,
			'clanky': ContentType.objects.get(app_label = 'article', model = 'article').pk,
			'spravy': ContentType.objects.get(app_label = 'news', model = 'news').pk,
			'anketa': ContentType.objects.get(app_label = 'survey', model = 'survey').pk,
		}


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

	def unescape(self, s):
		s = s.replace("&lt;", "<")
		s = s.replace("&gt;", ">")
		s = s.replace("&amp;", "&")
		return s

	def handle(self, *args, **kwargs):
		self.cursor = connections["linuxos"].cursor()
		self.import_users()
		self.import_articles()
		self.import_forum()
		self.import_news()
		self.import_survey()
		self.import_discussion()

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
		self.cursor.execute('SELECT COUNT(*) FROM users WHERE prava > 0')
		count = self.cursor.fetchall()[0][0]
		counter = 0
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM users WHERE prava > 0')
		sys.stdout.write("Importing users\n")
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
		self.import_article_hitcount()
		self.import_article_images()

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
			}
			articles.append(Article(**clanok))
		Article.objects.bulk_create(articles)
		connections['default'].cursor().execute('SELECT setval(\'article_article_id_seq\', (SELECT MAX(id) FROM article_article));')

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
			hitcount.append(HitCount(content_object = article, hits = hitcount_map.get(article.pk, 0)))
		HitCount.objects.bulk_create(hitcount)

	def import_article_images(self):
		articles = Article.objects.exclude(image = '')[:]
		sys.stdout.write("Downloading articles\n")
		counter = 0;
		for article in articles:
			counter += 1;
			sys.stdout.write("{0} / {1}\r".format(counter, len(articles)))
			sys.stdout.flush()
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
		sys.stdout.write("Importing forum sections\n")
		sys.stdout.flush()
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
		connections['default'].cursor().execute('SELECT setval(\'forum_section_id_seq\', (SELECT MAX(id) FROM forum_section));')

	def import_forum_topics(self):
		users = set(map(lambda x: x['id'], User.objects.values('id')))
		cols = [
			'id',
			'sekcia',
			'username',
			'predmet',
			'text',
			'userid',
			'datetime'
		]
		self.cursor.execute('SELECT COUNT(*) FROM forum')
		count = self.cursor.fetchall()[0][0]
		counter = 0
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM forum')
		sys.stdout.write("Importing forum\n")
		sys.stdout.flush()
		topics = []
		for topic_row in self.cursor:
			counter += 1
			sys.stdout.write("{0} / {1}\r".format(counter, count))
			sys.stdout.flush()
			topic_dict = self.decode_cols_to_dict(cols, topic_row)
			topic = {
				'pk': topic_dict['id'],
				'section_id': topic_dict['sekcia'],
				'username': topic_dict['username'],
				'subject': topic_dict['predmet'],
				'text': topic_dict['text'],
				'time': topic_dict['datetime'],
			}
			if topic_dict['userid'] and topic_dict['userid'] in users:
				topic['user_id'] = topic_dict['userid']
			topics.append(ForumTopic(**topic))
			if counter % 1000 == 0:
				ForumTopic.objects.bulk_create(topics)
				topics = []
		ForumTopic.objects.bulk_create(topics)
		topics = []
		connections['default'].cursor().execute('SELECT setval(\'forum_topic_id_seq\', (SELECT MAX(id) FROM forum_topic));')

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
		count = self.cursor.fetchall()[0][0]
		counter = 0
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM spravy')
		sys.stdout.write("Importing news\n")
		sys.stdout.flush()
		news_objects = []
		for news_row in self.cursor:
			counter += 1
			sys.stdout.write("{0} / {1}\r".format(counter, count))
			sys.stdout.flush()
			news_dict = self.decode_cols_to_dict(cols, news_row)

			slug = str(news_dict['id'])
			if news_dict['predmet']:
				slug = create_unique_slug(slugify(news_dict['predmet'])[:45], all_slugs, 9999)
				all_slugs.add(slug)

			news = {
				'pk': news_dict['id'],
				'subject': news_dict['predmet'] if news_dict['predmet'] else '-',
				'slug': slug,
				'short_text': news_dict['sprava'],
				'long_text': news_dict['sprava'],
				'time': news_dict['time'],
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
		connections['default'].cursor().execute('SELECT setval(\'news_news_id_seq\', (SELECT MAX(id) FROM news_news));')

	def import_survey(self):
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
		sys.stdout.write("Importing surveys\n")
		sys.stdout.flush()
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM anketa')
		surveys = []
		for survey_row in self.cursor:
			survey_dict = self.decode_cols_to_dict(cols, survey_row)

			if survey_dict['article_id']:
				slug = 'article-' + str(survey_dict['article_id'])
				content_type = ContentType.objects.get_for_model(Article)
				object_id = survey_dict['article_id']
			else:
				slug = create_unique_slug(slugify(survey_dict['otazka'][:45]), all_slugs, 9999)
				content_type = None
				object_id = None
			all_slugs.add(slug)

			survey = {
				'pk': survey_dict['id'],
				'question': survey_dict['otazka'],
				'slug': slug,
				'checkbox': bool(survey_dict['checkbox']),
				'approved': bool(survey_dict['enabled']) and survey_dict['schvalena'] == 'yes',
				'active_from': survey_dict['od'],
				'answer_count': sum(int(x) if x else 0 for x in survey_dict['hlasovanie'].split('/')) if survey_dict['hlasovanie'] else 0,
				'content_type': content_type,
				'object_id': object_id,
			}
			surveys.append(Survey(**survey))
		surveys = dict([(survey.pk, survey) for survey in Survey.objects.bulk_create(surveys)])

		answers = []
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM anketa')
		for survey_row in self.cursor:
			survey_dict = self.decode_cols_to_dict(cols, survey_row)
			survey_answers = loads(bytes(survey_dict['odpovede'].encode('utf-8')), array_hook=OrderedDict)
			survey_answers = [unicode(a[1], encoding='utf-8') for a in survey_answers.iteritems()]
			survey_votes = [int(x) if x else 0 for x in survey_dict['hlasovanie'].split('/')] if survey_dict['hlasovanie'] else []
			while (len(survey_votes) < len(survey_answers)):
				survey_votes.append(0)
			items = zip(survey_answers, survey_votes)
			for item in items:
				answers.append(SurveyAnswer(survey = surveys[survey_dict['id']], answer = item[0], votes = item[1]))
		SurveyAnswer.objects.bulk_create(answers)
		connections['default'].cursor().execute('SELECT setval(\'survey_survey_id_seq\', (SELECT MAX(id) FROM survey_survey));')
		connections['default'].cursor().execute('SELECT setval(\'survey_answer_id_seq\', (SELECT MAX(id) FROM survey_answer));')

	def import_discussion(self):
		sys.stdout.write("Importing discussion\n")
		sys.stdout.flush()
		sys.stdout.write("Headers ...\n")
		sys.stdout.flush()
		self.import_discussion_headers()
		sys.stdout.write("Contents ...\n")
		sys.stdout.flush()
		self.import_discussion_comments()

	def import_discussion_headers(self):
		cols = [
			'diskusia_id',
			'kategoria',
			'last_time',
			'reakcii',
			'zamknute',
			'vyriesene',
		]
		self.cursor.execute('SELECT COUNT(*) FROM diskusia_header')
		count = self.cursor.fetchall()[0][0]
		counter = 0
		self.cursor.execute('SELECT ' + (', '.join(cols)) + ' FROM diskusia_header')
		root_header_objects = []
		unique_check = set()
		for header_row in self.cursor:
			counter += 1
			sys.stdout.write("{0} / {1}\r".format(counter, count))
			sys.stdout.flush()

			header_dict = self.decode_cols_to_dict(cols, header_row)
			if header_dict['kategoria'] == 'eshop':
				continue

			if (self.content_types[header_dict['kategoria']], header_dict['diskusia_id']) in unique_check:
				continue
			unique_check.add((self.content_types[header_dict['kategoria']], header_dict['diskusia_id']))

			header = {
				'last_comment': header_dict['last_time'],
				'comment_count': self.get_default_if_null(header_dict['reakcii'], 0),
				'is_locked': bool(header_dict['zamknute']),
				'is_resolved': bool(header_dict['vyriesene']),
				'content_type_id': self.content_types[header_dict['kategoria']],
				'object_id': header_dict['diskusia_id'],
			}
			root_header_objects.append(ThreadedRootHeader(**header))
			if counter % 1000 == 0:
				ThreadedRootHeader.objects.bulk_create(root_header_objects)
				root_header_objects = []
		ThreadedRootHeader.objects.bulk_create(root_header_objects)
		root_header_objects = []
		connections['default'].cursor().execute('SELECT setval(\'threaded_comments_rootheader_id_seq\', (SELECT MAX(id) FROM threaded_comments_rootheader));')

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
		users = map(self.decode_username_for_comment, User.objects.values('id', 'email', 'first_name', 'last_name', 'username'))
		cols = [
			'parent',
			'username',
			'userid',
			'predmet',
			'text',
			'time',
			'locked',
		]
		query = 'SELECT ' + (', '.join(['diskusia.' + col for col in cols])) + ', diskusia_header.diskusia_id FROM diskusia INNER JOIN diskusia_header ON (diskusia.diskusiaid = diskusia_header.id) WHERE diskusia_id = {0}'
		cols.append('diskusia_id')
		headers = ThreadedRootHeader.objects.values_list('id', 'content_type_id', 'object_id', 'is_locked')
		counter = 0
		for id, content_type_id, object_pk, is_locked in headers:
			counter += 1
			sys.stdout.write("{0} / {1}\r".format(counter, len(headers)))
			sys.stdout.flush()
			self.cursor.execute(query.format(object_pk))
			comment_objects = [Comment(
				comment = '-',
				user_name = '-',
				submit_date = datetime.now(),
				site_id = settings.SITE_ID,
				content_type_id = content_type_id,
				object_pk = object_pk
			)]
			comment_rows = list(self.cursor)
			for comment_row in comment_rows:
				comment_dict = self.decode_cols_to_dict(cols, comment_row)
				comment = {
					'comment': comment_dict['text'],
					'user_name': comment_dict['username'],
					'submit_date': comment_dict['time'],
					'site_id': settings.SITE_ID,
					'is_public': True,
					'is_removed': False,
					'content_type_id': content_type_id,
					'object_pk': object_pk
				}
				if comment_dict['userid'] and comment_dict['userid'] in users:
					comment['user_id'] = comment_dict['userid']
				comment_objects.append(Comment(**comment))
			django_comments = Comment.objects.bulk_create(comment_objects)
