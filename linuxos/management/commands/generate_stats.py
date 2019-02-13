# -*- coding: utf-8 -*-
import csv
from io import BytesIO

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db.models import Count, Q

from accounts.models import User


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

	def write_users(self):
		writer = CsvWriter('stats/user.csv')
		writer.write_row(['username', 'pk', 'articles', 'blogs', 'comments', 'desktops', 'topics', 'news', 'tweets', 'wkiki_pages'])

		users = (User.objects
			.annotate(
				articles=Count('article', distinct=True),
				blogs=Count('blog__posts', distinct=True),
				comments=Count('comment_comments', filter=Q(comment_comments__parent__isnull=False), distinct=True),
				desktops=Count('desktop', distinct=True),
				topics=Count('topic', distinct=True),
				news_count=Count('news', filter=Q(news__approved=True), distinct=True),
				tweets=Count('tweet', distinct=True),
				wkiki_pages=Count('page', distinct=True),
			)
			.values_list('username', 'pk', 'articles', 'blogs', 'comments', 'desktops', 'topics', 'news_count', 'tweets', 'wkiki_pages'))

		for user in users:
			writer.write_row(user)

		writer.close()
