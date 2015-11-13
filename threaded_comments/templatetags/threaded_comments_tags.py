# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from operator import or_

from django import template
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, F, Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django_jinja import library
from jinja2 import contextfunction
from mptt.templatetags import mptt_tags

from ..cache import header_cache
from ..models import RootHeader, UserDiscussionAttribute
from common_utils import iterify, get_meta
from common_utils.content_types import get_lookups
from threaded_comments.models import Comment


register = template.Library()


class DiscussionLoader:
	def __init__(self):
		self.target = None
		self.context = None

	@cached_property
	def target_ctype(self):
		return ContentType.objects.get_for_model(self.target)

	@cached_property
	def root_header(self):
		object_id = self.target.pk
		ctype = self.target_ctype
		return RootHeader.objects.get(content_type=ctype, object_id=object_id)

	def get_queryset(self):
		object_id = self.target.pk
		ctype = self.target_ctype
		if not object_id:
			return Comment.objects.none()

		queryset = Comment.objects.filter(
			content_type=ctype,
			object_id=object_id,
		)
		try:
			queryset[0]
		except IndexError:
			Comment.objects.get_or_create_root_comment(ctype, object_id)
			queryset = Comment.objects.filter(
				content_type=ctype,
				object_id=object_id,
			)
		queryset = queryset.select_related('user__rating')
		queryset = queryset.prefetch_related('attachments')
		queryset = queryset.annotate(attachment_count=Count('attachments'))
		queryset = queryset.defer(
			"original_comment",
			"user__rating__comments", "user__rating__articles", "user__rating__helped", "user__rating__news", "user__rating__wiki",
			"user__password", "user__filtered_info",
		)
		queryset = queryset.order_by('lft')

		return queryset

	def get_discussion_attribute(self):
		object_id = self.target.pk
		ctype = self.target_ctype
		header = RootHeader.objects.get(content_type=ctype, object_id=object_id)
		discussion_attribute = UserDiscussionAttribute.objects.get_or_create(user=self.context['user'], discussion=header)[0]
		return discussion_attribute

	def highlight_new(self, query_set):
		root_item = query_set.get(level=0)
		prev_new_item = root_item
		for comment in query_set:
			if comment.is_new:
				prev_new_item.next_new = comment.pk
				if prev_new_item != root_item:
					comment.prev_new = prev_new_item.pk
				prev_new_item = comment

	def update_discussion_attribute(self, discussion_attribute):
		discussion_attribute.time = timezone.now()
		discussion_attribute.save()

	def get_last_display_time(self, discussion_attribute):
		last_display_time = timezone.now()
		if discussion_attribute.time:
			last_display_time = discussion_attribute.time
		return last_display_time

	def load(self, context, target):
		self.target = target
		self.context = context
		attrib = None
		query_set = self.get_queryset()
		if 'user' in context and context['user'].is_authenticated():
			attrib = self.get_discussion_attribute()
			last_display_time = self.get_last_display_time(attrib)
			self.update_discussion_attribute(attrib)
			query_set = query_set.annotate(is_new=F(created__gte=last_display_time))
			self.highlight_new(query_set)
		root_item = query_set.get(level=0)
		setattr(query_set, 'root_item', root_item)
		setattr(query_set, 'root_header', self.root_header)
		if 'user' in context and context['user'].is_authenticated():
			setattr(query_set, 'user_attribute', attrib)
		return query_set


def load_user_discussion_attributes(headers, user):
	header_ids = [h['id'] for h in headers]
	user_attributes = UserDiscussionAttribute.objects \
		.filter(user=user, discussion__in=header_ids) \
		.values('discussion_id', 'time', 'watch')
	user_attributes = dict([(a['discussion_id'], a) for a in user_attributes])
	for header in headers:
		header.update(user_attributes.get(header['id'], {}))


def copy_attributes(obj, attributes):
	for name, value in attributes.iteritems():
		setattr(obj, name, value)


@contextfunction
@library.global_function
def add_discussion_attributes(context, *models):
	discussion_lookups, content_types = get_lookups(models)
	user = context['user'] if 'user' in context and context['user'].is_authenticated() else None

	discussion_lookups = {
		content_type: [obj for obj in id_list if (obj, content_type.pk) not in header_cache.cache or user is not None]
		for content_type, id_list in discussion_lookups.iteritems()
	}
	discussion_lookups = {
		content_type: id_list
		for content_type, id_list in discussion_lookups.iteritems() if id_list
	}

	if user is None:
		for model, content_type in zip(models, content_types):
			for obj in model:
				copy_attributes(obj, header_cache.cache.get((obj.pk, content_type.pk), {}))

	if not discussion_lookups:
		return ''

	headers = (RootHeader.objects
		.filter(reduce(or_, (Q(content_type=content_type, object_id__in=id_list) for content_type, id_list in discussion_lookups.iteritems()), Q()))
		.values('id', 'object_id', 'content_type_id', 'last_comment', 'comment_count', 'is_locked')
	)
	headers_dict = {(obj['object_id'], obj['content_type_id']): obj for obj in headers}

	if user is not None:
		load_user_discussion_attributes(headers, user)

	for model, content_type in zip(models, content_types):
		for obj in model:
			if hasattr(obj, 'last_comment'):
				continue
			header = headers_dict.get((obj.pk, content_type.pk), {})
			cache_data = {
				'last_comment': header.get('last_comment', None),
				'comment_count': header.get('comment_count', 0),
				'is_locked': header.get('is_locked', False),
				'rootheader_id': header.get('id', None),
				'discussion_display_time': header.get('time', None),
				'discusison_watch': None,
				'new_comments': None,
			}
			copy_attributes(obj, cache_data)
			obj.discussion_watch = header.get('watch', None)
			if obj.last_comment and obj.discussion_display_time:
				obj.new_comments = obj.discussion_display_time < obj.last_comment
			else:
				obj.new_comments = None
			if header:
				header_cache.cache[(obj.pk, content_type.pk)] = cache_data

	return ''


@contextfunction
@library.global_function
def add_discussion_attributes_heterogenous(context, object_list):
	objects_sorted = {}
	for instance in iterify(object_list):
		objects_sorted.setdefault(instance.__class__, [])
		objects_sorted[instance.__class__].append(instance)
	add_discussion_attributes(context, *objects_sorted.values())
	return ''


@library.global_function
def get_comments_for_item(item, display_last=False):
	return mark_safe(render_to_string("comments/comment_count.html", {'item': item, display_last: 'display_last'}))


@library.global_function
@contextfunction
def get_threaded_comments_list(context, target):
	loader = DiscussionLoader()
	return loader.load(context, target)


@library.global_function
@contextfunction
def render_threaded_comments_toplevel(context, target):
	context = dict(context)
	model_class = target.__class__
	templates = (
		"comments/{0}_{1}_comments_toplevel.html".format(*str(get_meta(model_class)).split('.')),
		"comments/{0}_comments_toplevel.html".format(get_meta(model_class).app_label),
		"comments/comments_toplevel.html",
	)
	context.update({"target": target})
	return mark_safe(render_to_string(templates, context))


library.filter(mptt_tags.tree_info)
register.assignment_tag(get_threaded_comments_list, takes_context=True)
