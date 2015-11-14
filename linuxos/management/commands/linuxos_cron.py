# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.management.base import BaseCommand
from django.db.models import Count, F
from django.utils import timezone

from accounts.models import UserRating, RATING_WEIGHTS
from article.models import Article
from attachment.models import TemporaryAttachment
from comments.models import Comment
from news.models import News
from wiki.models import Page as WikiPage


class Command(BaseCommand):
	args = ''
	help = 'Cron'

	def __init__(self, *args, **kwargs):
		super(Command, self).__init__(*args, **kwargs)

	def handle(self, *args, **kwargs):
		self.delete_old_attachments()
		self.update_user_ratings()
		self.delete_old_events()

	def delete_old_attachments(self):
		now = timezone.now()
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

		user_comments = Comment.objects.filter(user_id__isnull = False, is_removed = False, is_public = True).values('user_id').annotate(Count('pk')).order_by('user').values_list('user_id', 'pk__count')
		user_comments_changed = filter(lambda c: c[0] not in ratings or c[1] != ratings[c[0]]['comments'], user_comments)
		for user_id, comment_count in user_comments_changed:
			rating, created = UserRating.objects.get_or_create(user_id = user_id)
			rating.comments = comment_count
			rating.save()
		del(user_comments)
		del(user_comments_changed)

		user_articles = Article.objects.filter(author_id__isnull = False).values('author_id').annotate(Count('pk')).values_list('author_id', 'pk__count')
		user_articles_changed = filter(lambda c: c[0] not in ratings or c[1] != ratings[c[0]]['articles'], user_articles)
		for user_id, comment_count in user_articles_changed:
			rating, created = UserRating.objects.get_or_create(user_id = user_id)
			rating.articles = comment_count
			rating.save()
		del(user_articles)
		del(user_articles_changed)

		user_news = News.objects.filter(author_id__isnull = False, approved = True).values('author_id').annotate(Count('pk')).values_list('author_id', 'pk__count')
		user_news_changed = filter(lambda c: c[0] not in ratings or c[1] != ratings[c[0]]['news'], user_news)
		for user_id, comment_count in user_news_changed:
			rating, created = UserRating.objects.get_or_create(user_id = user_id)
			rating.news = comment_count
			rating.save()
		del(user_news)
		del(user_news_changed)

		user_wiki = WikiPage.objects.filter(last_author_id__isnull = False).values('last_author_id').annotate(Count('pk')).values_list('last_author_id', 'pk__count')
		user_wiki_changed = filter(lambda c: c[0] not in ratings or c[1] != ratings[c[0]]['news'], user_wiki)
		for user_id, comment_count in user_wiki_changed:
			rating, created = UserRating.objects.get_or_create(user_id = user_id)
			rating.wiki = comment_count
			rating.save()
		del(user_wiki)
		del(user_wiki_changed)

		UserRating.objects.update(rating = sum([(F(w[0]) * w[1]) for w in RATING_WEIGHTS.iteritems()]))

	def delete_old_events(self):
		from notifications.models import Event, Inbox

		now = timezone.now()
		old_date = now - datetime.timedelta(days=30)
		old_events = Event.objects.filter(time__lte=old_date)

		Inbox.objects.filter(event__in=old_events).delete()
		old_events.delete()
