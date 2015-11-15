# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from accounts.models import UserRating
from attachment.models import TemporaryAttachment
from comments.models import Comment


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


def update_user_ratings_comments():
	new_ratings = (Comment.objects
		.filter(user_id__isnull=False, is_removed=False, is_public=True)
		.order_by('user_id')
		.values('user_id')
		.annotate(comment_count=Count('pk'))
		.values_list('user_id', 'comment_count'))
	_update_rating_data(new_ratings, 'comments')
