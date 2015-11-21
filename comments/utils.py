# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction
from django.db.models import Count, Max

from . import signals
from .models import CommentFlag, RootHeader, Comment


def perform_flag_action(request, comment, comment_flag, action=None):
	flag, created = CommentFlag.objects.get_or_create(
		comment=comment,
		user=request.user,
		flag=comment_flag
	)
	if action:
		action(comment)
	signals.comment_was_flagged.send(
		sender=comment.__class__,
		comment=comment,
		flag=flag,
		created=created,
		request=request
	)


def perform_flag(request, comment):
	perform_flag_action(request, comment, CommentFlag.SUGGEST_REMOVAL)


def perform_delete(request, comment):
	def action(comment):
		comment.is_removed = True
		comment.save()
	perform_flag_action(request, comment, CommentFlag.MODERATOR_DELETION, action)


def perform_approve(request, comment):
	def action(comment):
		comment.is_removed = False
		comment.is_public = True
		comment.save()
	perform_flag_action(request, comment, CommentFlag.MODERATOR_APPROVAL, action)


def update_comments_header(sender, instance, **kwargs): #pylint: disable=unused-argument
	if instance.parent is None:
		root = instance
	else:
		root = Comment.objects.get(content_type=instance.content_type, object_id=instance.object_id, parent=None)

	statistics = Comment.objects.\
		filter(content_type=root.content_type, object_id=root.object_id, is_public=True, is_removed=False).\
		exclude(pk=root.pk).\
		aggregate(Count('pk'), Max('created'))

	last_comment = statistics['created__max']
	if last_comment is None:
		content_object = root.content_object
		last_comment = content_object.created

	with transaction.atomic():
		header, _ = RootHeader.objects.get_or_create(
			content_type=root.content_type,
			object_id=root.object_id,
			defaults={'pub_date': root.created, 'last_comment': last_comment}
		)
		header.is_locked = root.is_locked
		header.last_comment = last_comment
		header.pub_date = root.created
		header.comment_count = statistics['pk__count']
		header.save()
