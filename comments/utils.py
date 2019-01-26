# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction
from django.db.models import Count, Max

from .models import RootHeader, Comment


def update_comments_header(sender, instance, **kwargs): #pylint: disable=unused-argument
	try:
		if instance.parent is None:
			root = instance
		else:
			root = Comment.objects.get(content_type=instance.content_type, object_id=instance.object_id, parent=None)
	except Comment.DoesNotExist:
		return

	statistics = (Comment.objects.
		filter(content_type=root.content_type, object_id=root.object_id, is_public=True, is_removed=False).
		exclude(pk=root.pk).
		aggregate(Count('pk'), Max('created')))

	last_comment = statistics['created__max']
	if last_comment is None:
		content_object = root.content_object
		if content_object is None:
			return
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
		return header
