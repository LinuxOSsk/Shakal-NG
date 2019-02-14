# -*- coding: utf-8 -*-
import csv
from collections import namedtuple
from datetime import timedelta
from io import BytesIO

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db import models
from django.db.models import Count, Q, F, Value as V, Subquery, OuterRef
from django.db.models.functions import Concat, Coalesce
from django.utils import timezone

from accounts.models import User
from article.models import Article
from blog.models import Post as BlogPost
from comments.models import Comment
from common_utils.time_series import time_series
from desktops.models import Desktop
from forum.models import Topic
from news.models import News
from tweets.models import Tweet
from wiki.models import Page as WikiPage


START_DATE = timezone.datetime(2004, 1, 1, tzinfo=timezone.utc)


ContentModel = namedtuple('ContentModel', ['model', 'label', 'author', 'username', 'select_filter', 'reverse_name'])


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
		self.write_time_series()
		fp = default_storage.open('./stats/links.txt', 'w')
		fp.write("./user.csv - users stats, years: all\n")
		for year in (1, 2, 5):
			fp.write("./user_%d_year.csv - users stats, years: %d\n" % (year, year))
		for content_model in self.get_content_models():
			fp.write("./%s_table.csv - table of %s objects\n" % (content_model.label, content_model.label))
		for interval in ('month', 'week', 'day'):
			fp.write("./series_%s.csv - statistics for interval %s\n" % (interval, interval))
		fp.close()

	def get_content_models(self):
		now = timezone.now()
		return (
			ContentModel(
				Article, 'articles',
				author='author',
				username='authors_name',
				select_filter=Q(published=True, pub_time__lte=now),
				reverse_name='article'
			),
			ContentModel(
				BlogPost, 'blogs',
				author='blog__author',
				username=None,
				select_filter=Q(pub_time__lte=now),
				reverse_name='blog__post'
			),
			ContentModel(
				Comment, 'comments',
				author='user',
				username='user_name',
				select_filter=Q(parent__isnull=False, is_public=True, is_removed=False),
				reverse_name='comment_comments'
			),
			ContentModel(
				Desktop, 'desktops',
				author='author',
				username=None,
				select_filter=None,
				reverse_name='desktop'
			),
			ContentModel(
				Topic, 'topics',
				author='author',
				username='authors_name',
				select_filter=None,
				reverse_name='topic'
			),
			ContentModel(
				News, 'news',
				author='author',
				username='authors_name',
				select_filter=Q(approved=True),
				reverse_name='news'
			),
			ContentModel(
				Tweet, 'tweets',
				author='author',
				username=None,
				select_filter=None,
				reverse_name='tweet'
			),
			ContentModel(
				WikiPage, 'wiki_pages',
				author='last_author',
				username=None,
				select_filter=None,
				reverse_name='page'
			),
		)

	def get_user_stats(self, date_start=None):
		users = User.objects.order_by('pk').values('username', 'pk')
		fields = []
		for content_model in self.get_content_models():
			if not content_model.author or not content_model.reverse_name:
				continue
			date_filter = Q()
			if date_start:
				date_filter = Q(created__range=[date_start - timedelta(365000), timezone.now()])
			count = Subquery(content_model.model._default_manager
				.filter(date_filter)
				.filter(**{content_model.author: OuterRef('pk')})
				.values(content_model.author)
				.annotate(cnt=Count(content_model.author)).values('cnt')[:1], output_field=models.IntegerField())
			users = users.annotate(**{'count_'+content_model.label: Coalesce(count, V(0, output_field=models.IntegerField()))})
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

		extra_queryset = self.call_extra_model_action(content_model, 'get_extra_queryset', queryset)
		if extra_queryset is not None:
			queryset = extra_queryset
		extra_header_fields = self.call_extra_model_action(content_model, 'get_extra_header') or []
		header = header + extra_header_fields
		extra_values = self.call_extra_model_action(content_model, 'get_extra_fields') or []
		fields = fields + extra_values

		writer = CsvWriter('stats/%s_table.csv' % content_model.label)
		writer.write_row(header)
		for row in queryset.values_list(*fields):
			date_field = field_map['created']
			csv_row = list(row)
			csv_row[date_field] = csv_row[date_field].replace(microsecond=0).isoformat()
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

	def write_time_series(self):
		end_date = timezone.now()
		content_models = self.get_content_models()
		fields = [content_model.label for content_model in content_models]

		for interval in ('month', 'week', 'day'):
			stats = {}
			for content_model in content_models:
				queryset = content_model.model._default_manager.order_by('pk')
				if content_model.select_filter:
					queryset = queryset.filter(content_model.select_filter)

				ts = time_series(
					queryset,
					date_field='created',
					aggregate={'count': Count('id')},
					interval=interval,
					date_from=START_DATE,
					date_to=end_date
				)
				stats[content_model.label] = ts

			writer = CsvWriter('stats/series_%s.csv' % interval)
			writer.write_row(['date'] + fields)
			for row in zip(*[stats[field] for field in fields]):
				csv_row = [row[0].time_value.isoformat()] + [col.count or 0 for col in row]
				writer.write_row(csv_row)
			writer.close()

	def call_extra_model_action(self, content_model, action, *args, **kwargs):
		app_label = content_model.model._meta.app_label
		model_name = content_model.model._meta.model_name
		method = '%s_%s_%s' % (action, app_label, model_name)
		if hasattr(self, method):
			return getattr(self, method)(*args, **kwargs)

	def get_extra_queryset_comments_comment(self, queryset):
		return queryset.annotate(
			object_type=Concat(F('content_type__app_label'), V('_'), F('content_type__model'))
		)

	def get_extra_header_comments_comment(self):
		return ['parent', 'depth', 'type', 'object_id']

	def get_extra_fields_comments_comment(self):
		return ['parent', 'level', 'object_type', 'object_id']
