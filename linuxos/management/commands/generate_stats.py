# -*- coding: utf-8 -*-
import csv
from collections import namedtuple
from io import BytesIO

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from accounts.models import User
from article.models import Article
from blog.models import Post as BlogPost
from comments.models import Comment
from desktops.models import Desktop
from forum.models import Topic
from news.models import News
from tweets.models import Tweet
from wiki.models import Page as WikiPage


ContentModel = namedtuple('ContentModel', ['model', 'label', 'author', 'username', 'select_filter', 'agg_filter', 'agg_filter_date', 'reverse_name'])



class CsvWriter(object):
	def __init__(self, path):
		self.path = path
		if default_storage.exists(self.path + '.tmp'):
			default_storage.delete(self.path + '.tmp')
		default_storage.save(self.path + '.tmp', BytesIO())
		self.fp = default_storage.open(self.path + '.tmp', 'w')
		self.writer = csv.writer(self.fp)

	def write_row(self, row):
		self.writer.writerow(row)

	def close(self):
		self.fp.close()
		if default_storage.exists(self.path):
			default_storage.delete(self.path)
		tmp_fp = default_storage.open(self.path + '.tmp', 'r')
		default_storage.save(self.path, tmp_fp)
		default_storage.delete(self.path + '.tmp')


class Command(BaseCommand):
	help = "Generate statistics"

	def handle(self, *args, **options):
		self.write_users()
		self.write_models()
		fp = default_storage.open('stats/links.txt', 'w')
		fp.write("users.csv - users stats, years: all\n")
		for year in (1, 2, 5):
			fp.write("users_%d_year.csv - users stats, years: %d\n" % (year, year))
		for content_model in self.get_content_models():
			fp.write("%s_table.csv - table of %s objects\n" % (content_model.label, content_model.label))
		fp.close()

	def get_content_models(self):
		now = timezone.now()
		return (
			ContentModel(
				Article, 'articles',
				author='author',
				username='authors_name',
				select_filter=Q(published=True, pub_time__lte=now),
				agg_filter=Q(article__published=True, article__pub_time__lte=now),
				agg_filter_date=lambda date_range: Q(article__created__range=date_range),
				reverse_name='article'
			),
			ContentModel(
				BlogPost, 'blogs',
				author='blog__author',
				username=None,
				select_filter=Q(pub_time__lte=now),
				agg_filter=Q(blog__post__pub_time__lte=now),
				agg_filter_date=lambda date_range: Q(blog__post__created__range=date_range),
				reverse_name='blog__posts'
			),
			ContentModel(
				Comment, 'comments',
				author='user',
				username='user_name',
				select_filter=Q(parent__isnull=False, is_public=True, is_removed=False),
				agg_filter=Q(comment_comments__parent__isnull=False, comment_comments__is_public=True, comment_comments__is_removed=False),
				agg_filter_date=lambda date_range: Q(comment_comments__created__range=date_range),
				reverse_name='comment_comments'
			),
			ContentModel(
				Desktop, 'desktops',
				author='author',
				username=None,
				select_filter=None,
				agg_filter=None,
				agg_filter_date=lambda date_range: Q(desktop__created__range=date_range),
				reverse_name='desktop'
			),
			ContentModel(
				Topic, 'topics',
				author='author',
				username='authors_name',
				select_filter=None,
				agg_filter=None,
				agg_filter_date=lambda date_range: Q(topic__created__range=date_range),
				reverse_name='topic'
			),
			ContentModel(
				News, 'news',
				author='author',
				username='authors_name',
				select_filter=Q(approved=True),
				agg_filter=Q(news__approved=True),
				agg_filter_date=lambda date_range: Q(news__created__range=date_range),
				reverse_name='news'
			),
			ContentModel(
				Tweet, 'tweets',
				author='author',
				username=None,
				select_filter=None,
				agg_filter=None,
				agg_filter_date=lambda date_range: Q(tweet__created__range=date_range),
				reverse_name='tweet'
			),
			ContentModel(
				WikiPage, 'wiki_pages',
				author='last_author',
				username=None,
				select_filter=None,
				agg_filter=None,
				agg_filter_date=lambda date_range: Q(page__created__range=date_range),
				reverse_name='page'
			),
		)

	def get_user_stats(self, date_start=None):
		users = User.objects.order_by('pk').values('username', 'pk')
		fields = []
		for content_model in self.get_content_models():
			if not content_model.author or not content_model.reverse_name:
				continue
			agg_filter = content_model.agg_filter or Q()
			if date_start:
				if content_model.agg_filter_date is None:
					continue
				agg_filter = agg_filter & content_model.agg_filter_date([date_start, timezone.now()])
			count = Count(content_model.reverse_name, distinct=True, filter=agg_filter)
			users = users.annotate(**{'count_'+content_model.label: count})
			fields.append(content_model.label)
		return users.values_list('username', 'pk', *['count_'+label for label in fields]), fields

	def write_users(self):
		users, fields = self.get_user_stats()
		writer = CsvWriter('stats/user.csv')
		writer.write_row(['username', 'pk'] + fields)
		for user in users:
			writer.write_row(user)
		writer.close()

		for year in (1, 2, 5):
			start_date = timezone.now() - timedelta(days=365*year)
			users, fields = self.get_user_stats(start_date)
			writer = CsvWriter('stats/user_%d_year.csv' % year)
			writer.write_row(['username', 'pk'] + fields)
			for user in users:
				writer.write_row(user)
			writer.close()

	def write_models(self):
		for content_model in self.get_content_models():
			self.write_model(content_model)

	def write_model(self, content_model):
		self.write_model_table(content_model)

	def write_model_table(self, content_model):
		header = ['pk', 'created']
		fields = ['pk', 'created']
		if content_model.author:
			header.append('user_id')
			fields.append(content_model.author)
		if content_model.username:
			header.append('username')
			fields.append(content_model.username)
		field_map = {field: i for i, field in enumerate(header)}

		queryset = content_model.model._default_manager.order_by('pk')
		if content_model.select_filter:
			queryset = queryset.filter(content_model.select_filter)

		writer = CsvWriter('stats/%s_table.csv' % content_model.label)
		writer.write_row(header)
		for row in queryset.values_list(*fields):
			date_field = field_map['created']
			csv_row = list(row)
			csv_row[date_field] = csv_row[date_field].isoformat()
			if 'username' in field_map and 'user_id' in field_map:
				username = csv_row[field_map['username']]
				user_id = csv_row[field_map['user_id']]
				if user_id is None:
					user_id = ''
				else:
					username = ''
				csv_row[field_map['username']] = username
				csv_row[field_map['user_id']] = user_id
			writer.write_row(csv_row)
		writer.close()
