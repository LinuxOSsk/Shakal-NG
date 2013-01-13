# -*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.contrib.comments.templatetags.comments import BaseCommentNode
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from datetime import datetime
from shakal import threaded_comments
from shakal.threaded_comments.models import RootHeader, UserDiscussionAttribute

register = template.Library()


class ThreadedCommentsBaseNode(BaseCommentNode):
	def __init__(self, *args, **kwargs):
		super(ThreadedCommentsBaseNode, self).__init__(*args, **kwargs)
		self.root_node = None
		self.comments_model = threaded_comments.get_model()

	def get_root_node(self, context):
		if self.root_node is None:
			ctype, object_pk = self.get_target_ctype_pk(context)
			self.root_node, created = self.comments_model.objects.get_root_comment(ctype, object_pk)
		return self.root_node

	def get_comments_query_set(self, context):
		ctype, object_pk = self.get_target_ctype_pk(context)
		if not object_pk:
			return self.comments_model.comment_objects.none()

		queryset = self.comments_model.comment_objects.filter(
			content_type = ctype,
			object_pk = object_pk,
			site__pk = settings.SITE_ID,
		).filter(Q(parent = None) | Q(is_public = True, is_removed = False))
		queryset = queryset.order_by('lft')
		return queryset

	def get_query_set(self, context):
		ctype, object_pk = self.get_target_ctype_pk(context)
		queryset = self.get_comments_query_set(context)
		if not queryset.has_root_item():
			self.comments_model.objects.get_root_comment(ctype, object_pk)
			queryset = self.get_comments_query_set(context)
		return queryset


class ThreadedCommentsListNode(ThreadedCommentsBaseNode):
	def highlight_new(self, query_set, context):
		root_item = query_set.get_root_item()
		prev_new_item = root_item;
		for comment in query_set:
			if comment.is_new:
				prev_new_item.next_new = comment.pk
				if prev_new_item != root_item:
					comment.prev_new = prev_new_item.pk
				prev_new_item = comment

	def get_discussion_attribute(self, context):
		ctype, object_pk = self.get_target_ctype_pk(context)
		header = RootHeader.objects.get(content_type = ctype, object_id = object_pk)
		(discussion_attribute, created) = UserDiscussionAttribute.objects.get_or_create(user = context['user'], discussion = header)
		return discussion_attribute

	def update_discussion_attribute(self, discussion_attribute):
		discussion_attribute.time = datetime.now()
		discussion_attribute.save()

	def get_last_display_time(self, discussion_attribute):
		last_display_time = datetime.now()
		if discussion_attribute.time:
			last_display_time = discussion_attribute.time
		return last_display_time

	def render(self, context):
		query_set = self.get_query_set(context)
		if 'user' in context and context['user'].is_authenticated():
			attrib = self.get_discussion_attribute(context)
			last_display_time = self.get_last_display_time(attrib)
			self.update_discussion_attribute(attrib)
			query_set = query_set.extra(select = {'is_new': 'submit_date >= %s'}, select_params = (last_display_time, ))[:]
			self.highlight_new(query_set, context)
		context[self.as_varname] = query_set
		return ''


class ThreadedCommentsFormNode(ThreadedCommentsBaseNode):
	def get_form(self, context):
		ctype, object_pk = self.get_target_ctype_pk(context)
		if object_pk:
			return threaded_comments.get_form()(ctype.get_object_for_this_type(pk=object_pk), parent_comment=self.get_root_node(context))
		else:
			return None

	def render(self, context):
		context[self.as_varname] = self.get_form(context)
		return ''


@register.tag
def get_threaded_comments_list(parser, token):
	return ThreadedCommentsListNode.handle_token(parser, token)


@register.simple_tag(takes_context = True)
def render_threaded_comments_toplevel(context, target):
	model_class = target.__class__
	templates = [
		"comments/{0}_{1}_comments_toplevel.html".format(*str(model_class._meta).split('.')),
		"comments/{0}_comments_toplevel.html".format(model_class._meta.app_label),
		"comments/comments_toplevel.html".format(model_class._meta.app_label),
	]
	context.update({"target": target})
	return mark_safe(render_to_string(templates, context))


@register.simple_tag
def get_comments_for_item(item, display_last = False):
	template = "comments/comment_count.html"
	return mark_safe(render_to_string(template, {'item': item, 'display_last': display_last}))


@register.simple_tag(takes_context = True)
def add_discussion_attributes(context, model):
	try:
		iter(model)
	except TypeError:
		model = [model]
	content_type = None
	id_list = []
	for obj in model:
		id_list.append(obj.pk)
		if content_type is None:
			content_type = ContentType.objects.get_for_model(type(obj))
	if not content_type:
		return ''
	headers = RootHeader.objects
	headers = headers.filter(content_type = content_type, object_id__in = id_list)
	headers = headers.values(
		'id',
		'object_id',
		'last_comment',
		'comment_count',
		'is_locked',
	)
	if 'user' in context and context['user'].is_authenticated():
		header_ids = [h['id'] for h in headers]
		user_attributes = UserDiscussionAttribute.objects
		user_attributes = user_attributes.filter(user = context['user'], discussion__in = header_ids)
		user_attributes = user_attributes.values('discussion_id', 'time', 'watch')
		user_attributes = dict([(a['discussion_id'], a) for a in user_attributes])
		for header in headers:
			header.update(user_attributes.get(header['id'], {}))
	headers = dict([(h['object_id'], h) for h in headers])
	for obj in model:
		hdr = headers.get(obj.pk, {})
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
