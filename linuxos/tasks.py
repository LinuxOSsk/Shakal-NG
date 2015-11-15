# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from accounts.models import UserRating
from article.models import Article
from attachment.models import TemporaryAttachment
from comments.models import Comment
from news.models import News
from wiki.models import Page as WikiPage


def _update_rating_data(new_ratings, field_name):
	current_ratings = dict(UserRating.objects.values_list('user_id', field_name))
	for user_id, count in new_ratings:
		if count != current_ratings.get(user_id, 0):
			UserRating.objects.update_or_create(user_id=user_id, defaults={field_name: count})


def delete_old_attachments():
	old_attachments = (TemporaryAttachment.objects
		.filter(created__lt=timezone.now() - timedelta(1)))
	for old_attachment in old_attachments:
		old_attachment.delete()


def update_user_ratings():
	update_user_ratings_comments()
	update_user_ratings_articles()
	update_user_ratings_news()
	update_user_ratings_wiki()


def update_user_ratings_comments():
	ratings = (Comment.objects
		.filter(user_id__isnull=False, is_removed=False, is_public=True)
		.order_by('user_id')
		.values('user_id')
		.annotate(comment_count=Count('pk'))
		.values_list('user_id', 'comment_count'))
	_update_rating_data(ratings, 'comments')


def update_user_ratings_articles():
	ratings = (Article.objects
		.filter(author_id__isnull=False)
		.order_by('author_id')
		.values('author_id')
		.annotate(articles_count=Count('pk'))
		.values_list('author_id', 'articles_count'))
	_update_rating_data(ratings, 'articles')


def update_user_ratings_news():
	ratings = (News.objects
		.filter(author_id__isnull=False, approved=True)
		.order_by('author_id')
		.values('author_id')
		.annotate(news_count=Count('pk'))
		.values_list('author_id', 'news_count'))
	_update_rating_data(ratings, 'news')


def update_user_ratings_wiki():
	ratings = (WikiPage.objects
		.filter(last_author_id__isnull=False)
		.order_by('last_author_id')
		.values('last_author_id')
		.annotate(wiki_count=Count('pk'))
		.values_list('last_author_id', 'wiki_count'))
	_update_rating_data(ratings, 'wiki')
