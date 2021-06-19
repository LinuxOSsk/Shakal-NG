# -*- coding: utf-8 -*-
from datetime import timedelta

from django.db.models import Count, F
from django.utils import timezone

from accounts.models import UserRating
from article.models import Article
from attachment.models import UploadSession
from comments.models import Comment
from news.models import News
from notifications.models import Event, Inbox
from wiki.models import Page as WikiPage


def delete_old_attachments():
	old_sessions = (UploadSession.objects
		.filter(created__lt=timezone.now() - timedelta(1)))
	for old_session in old_sessions:
		for attachment in old_session.attachments.all():
			attachment.delete()
		old_session.delete()


def delete_old_events():
	old_events = Event.objects.filter(time__lte=timezone.now() - timedelta(30))
	Inbox.objects.filter(event__in=old_events).delete()
	old_events.delete()


def update_user_ratings():
	update_user_ratings_comments()
	update_user_ratings_articles()
	update_user_ratings_news()
	update_user_ratings_wiki()
	update_user_ratings_sum()


def _update_rating_data(new_ratings, field_name, author_field):
	new_ratings_stats = (new_ratings
		.order_by(author_field)
		.values(author_field)
		.annotate(cnt=Count('pk'))
		.values_list(author_field, 'cnt'))

	current_ratings = dict(UserRating.objects.values_list('user_id', field_name))
	for user_id, count in new_ratings_stats:
		if count != current_ratings.get(user_id, 0):
			UserRating.objects.update_or_create(user_id=user_id, defaults={field_name: count})


def update_user_ratings_comments():
	ratings = (Comment.objects
		.filter(user_id__isnull=False, is_removed=False, is_public=True))
	_update_rating_data(ratings, 'comments', 'user_id')


def update_user_ratings_articles():
	ratings = (Article.objects
		.filter(author_id__isnull=False))
	_update_rating_data(ratings, 'articles', 'author_id')


def update_user_ratings_news():
	ratings = (News.objects
		.filter(author_id__isnull=False, approved=True))
	_update_rating_data(ratings, 'news', 'author_id')


def update_user_ratings_wiki():
	ratings = (WikiPage.objects
		.filter(last_author_id__isnull=False))
	_update_rating_data(ratings, 'wiki', 'last_author_id')


def update_user_ratings_sum():
	UserRating.objects.update(
		rating=sum([(F(column) * weight) for column, weight in UserRating.RATING_WEIGHTS.items()])
	)


def fix_duplicate_headers():
	duplicate_content_types = (Comment.objects
		.filter(level=0)
		.values('content_type', 'object_id')
		.order_by('content_type', 'object_id')
		.annotate(cnt=Count('id'))
		.filter(cnt__gt=1))

	for content in duplicate_content_types:
		roots = (Comment.objects
			.filter(object_id=content['object_id'], content_type=content['content_type'], level=0))
		first_root = None

		for root in roots:
			child_nodes = Comment.objects.filter(parent=root)
			if child_nodes.count() == 0:
				root.delete()
			else:
				if first_root is None:
					first_root = root
				else:
					for node in list(child_nodes):
						node.move_to(first_root, 'last-child')
					root.delete()
