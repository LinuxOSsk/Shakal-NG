# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django_jinja import library
from jinja2 import contextfunction
from mptt.templatetags import mptt_tags

from ..models import RootHeader, UserDiscussionAttribute
from common_utils import get_meta
from common_utils.content_types import get_lookups
from threaded_comments.models import Comment


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
			query_set = query_set.extra(select={'is_new': 'submit_date >= %s'}, select_params=(last_display_time, ))[:]
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


@contextfunction
@library.global_function
def add_discussion_attributes(context, *models):
	discussion_lookups, content_types = get_lookups(models)

	# odstránenie prázdnych
	#discussion_lookups = {content_type: [i for i in id_list if (i, content_type.pk) not in cache] for content_type, id_list in discussion_lookups.iteritems()}
	discussion_lookups = {content_type: id_list for content_type, id_list in discussion_lookups.iteritems() if id_list}

	if not discussion_lookups:
		return ''

	discussion_q = Q()
	for content_type, ids in discussion_lookups.iteritems():
		discussion_q = discussion_q | Q(content_type=content_type, object_id__in=ids)

	headers = RootHeader.objects \
		.filter(discussion_q) \
		.values('id', 'object_id', 'content_type_id', 'last_comment', 'comment_count', 'is_locked')
	headers_dict = {(h['object_id'], h['content_type_id']): h for h in headers}

	if 'user' in context and context['user'].is_authenticated():
		load_user_discussion_attributes(headers, context['user'])

	for model, content_type in zip(models, content_types):
		for obj in model:
			key = (obj.pk, content_type.pk)
			header = headers_dict.get(key, {})
			obj.last_comment = header.get('last_comment', None)
			obj.comment_count = header.get('comment_count', 0)
			obj.is_locked = header.get('is_locked', False)
			obj.rootheader_id = header.get('id', None)
			obj.discussion_display_time = header.get('time', None)
			obj.discussion_watch = header.get('watch', None)
			if obj.last_comment and obj.discussion_display_time:
				obj.new_comments = obj.discussion_display_time < obj.last_comment
			else:
				obj.new_comments = None

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
