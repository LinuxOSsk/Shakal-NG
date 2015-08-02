# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django_jinja import library
from jinja2 import contextfunction

from ..models import RootHeader, UserDiscussionAttribute
from common_utils.content_types import get_lookups


@contextfunction
@library.global_function
def add_discussion_attributes(context, *models):
	discussion_lookups, content_types = get_lookups(models)

	# odstránenie prázdnych
	#discussion_lookups = {content_type: [i for i in id_list if (i, content_type.pk) not in cache] for content_type, id_list in discussion_lookups.iteritems()}
	discussion_lookups = {content_type: id_list for content_type, id_list in discussion_lookups.iteritems() if id_list}

	if not discussion_lookups:
		return ''

	discussion_q = None
	for content_type, ids in discussion_lookups.iteritems():
		q = Q(content_type=content_type, object_id__in=ids)
		discussion_q = q if discussion_q is None else discussion_q | q

	headers = RootHeader.objects \
		.filter(discussion_q) \
		.values('id', 'object_id', 'content_type_id', 'last_comment', 'comment_count', 'is_locked')
	headers_dict = {(h['object_id'], h['content_type_id']): h for h in headers}

	if 'user' in context and context['user'].is_authenticated():
		header_ids = [h['id'] for h in headers]
		user_attributes = UserDiscussionAttribute.objects \
			.filter(user=context['user'], discussion__in=header_ids) \
			.values('discussion_id', 'time', 'watch')
		user_attributes = dict([(a['discussion_id'], a) for a in user_attributes])
		for header in headers:
			header.update(user_attributes.get(header['id'], {}))

	for model, content_type in zip(models, content_types):
		for obj in model:
			key = (obj.pk, content_type.pk)
			hdr = headers_dict.get(key, {})
			obj.last_comment = hdr.get('last_comment', None)
			obj.comment_count = hdr.get('comment_count', 0)
			obj.is_locked = hdr.get('is_locked', False)
			obj.rootheader_id = hdr.get('id', None)
			obj.discussion_display_time = hdr.get('time', None)
			obj.discussion_watch = hdr.get('watch', None)
			if obj.last_comment and obj.discussion_display_time:
				obj.new_comments = obj.discussion_display_time < obj.last_comment
			else:
				obj.new_comments = None

	return ''


@library.global_function
def get_comments_for_item(item, display_last=False):
	return mark_safe(render_to_string("comments/comment_count.html", {'item': item, display_last: 'display_last'}))
