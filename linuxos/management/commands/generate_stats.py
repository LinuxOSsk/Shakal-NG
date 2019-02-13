# -*- coding: utf-8 -*-
import csv
from collections import namedtuple
from io import BytesIO

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone

from accounts.models import User
from article.models import Article
from blog.models import Post as BlogPost
from comments.models import Comment
from desktops.models import Desktop
from forum.models import Topic
from news.models import News
from tweets.models import Tweet
from wiki.models import Page as WikiPage


ContentModel = namedtuple('ContentModel', ['model', 'label', 'author', 'username', 'date', 'agg_filter', 'reverse_name'])



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


class Command(BaseCommand):
	help = "Generate statistics"

	def handle(self, *args, **options):
		self.write_users()

	def get_content_models(self):
		now = timezone.now()
		return (
			ContentModel(
				Article, 'articles',
				author='author',
				username='authors_name',
				date='created',
				agg_filter=Q(article__published=True, article__pub_time__lte=now),
				reverse_name='article'
			),
			ContentModel(
				BlogPost, 'blogs',
				author='blog__author',
				username=None,
				date='created',
				agg_filter=Q(blog__post__pub_time__lte=now),
				reverse_name='blog__posts'
			),
			ContentModel(
				Comment, 'comments',
				author='user',
				username='user_name',
				date='created',
				agg_filter=Q(comment_comments__parent__isnull=False, comment_comments__is_public=True, comment_comments__is_removed=False),
				reverse_name='comment_comments'
			),
			ContentModel(
				Desktop, 'desktops',
				author='author',
				username=None,
				date='created',
				agg_filter=None,
				reverse_name='desktop'
			),
			ContentModel(
				Topic, 'topics',
				author='author',
				username='authors_name',
				date='created',
				agg_filter=None,
				reverse_name='topic'
			),
			ContentModel(
				News, 'news',
				author='author',
				username='authors_name',
				date='created',
				agg_filter=Q(news__approved=True),
				reverse_name='news'
			),
			ContentModel(
				Tweet, 'tweets',
				author='author',
				username=None,
				date='created',
				agg_filter=None,
				reverse_name='tweet'
			),
			ContentModel(
				WikiPage, 'wiki_pages',
				author='last_author',
				username=None,
				date='created',
				agg_filter=None,
				reverse_name='page'
			),
		)

	def write_users(self):
		logged_users_stats = User.objects.order_by('pk').values('username', 'pk')
		fields = []
		for content_model in self.get_content_models():
			if not content_model.author or not content_model.reverse_name:
				continue
			count = Count(content_model.reverse_name, distinct=True, filter=content_model.agg_filter)
			logged_users_stats = logged_users_stats.annotate(**{'count_'+content_model.label: count})
			fields.append(content_model.label)

		logged_users_stats = logged_users_stats.values_list('username', 'pk', *['count_'+label for label in fields])

		writer = CsvWriter('stats/user.csv')
		writer.write_row(['username', 'pk'] + fields)
		for user in logged_users_stats:
			writer.write_row(user)
		writer.close()
