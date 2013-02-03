# -*- coding: utf-8 -*-

from attachment.models import TemporaryAttachment
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.db.models import Count
from shakal.accounts.models import UserRating
from shakal.article.models import Article

class Command(BaseCommand):
	args = ''
	help = 'Cron'

	def __init__(self, *args, **kwargs):
		super(Command, self).__init__(*args, **kwargs)

	def handle(self, *args, **kwargs):
		self.delete_old_attachments()
		self.update_user_ratings()

	def delete_old_attachments(self):
		now = datetime.datetime.now()
		old_date = now - datetime.timedelta(days = 1)
		old_attachments = TemporaryAttachment.objects.filter(created__lt = old_date)[:]
		for old_attachment in old_attachments:
			old_attachment.delete()

	def update_user_ratings(self):
		columns = (
			'user',
			'comments',
			'articles',
			'helped',
			'news',
			'wiki'
		)
		ratings = UserRating.objects.values_list(*columns)
		ratings = [dict(zip(columns, r)) for r in ratings]
		ratings = dict([(r['user'], r) for r in ratings])

		user_comments = Comment.objects.filter(user_id__isnull = False, is_removed = False, is_public = True).values('user_id').annotate(num_comments = Count('pk')).order_by('user').values_list('user_id', 'num_comments')
		user_comments_changed = filter(lambda c: c[0] not in ratings or c[1] != ratings[c[0]]['comments'], user_comments)
		for user_id, comment_count in user_comments_changed:
			rating, created = UserRating.objects.get_or_create(user_id = user_id)
			rating.comments = comment_count
			rating.save()
		del(user_comments)
		del(user_comments_changed)

		user_articles = Article.objects.filter(author_id__isnull = False, published = True).values('author_id').annotate(num_articles = Count('pk')).order_by('author').values_list('author_id', 'num_articles')
		user_articles_changed = filter(lambda c: c[0] not in ratings or c[1] != ratings[c[0]]['articles'], user_articles)
		for user_id, comment_count in user_articles_changed:
			rating, created = UserRating.objects.get_or_create(user_id = user_id)
			rating.articles = comment_count
			rating.save()
		del(user_articles)
		del(user_articles_changed)
