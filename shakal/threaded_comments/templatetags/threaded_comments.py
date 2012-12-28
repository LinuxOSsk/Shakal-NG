# -*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.contrib.comments.templatetags.comments import BaseCommentNode
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from datetime import datetime
from shakal import threaded_comments

register = template.Library()


class ThreadedCommentsBaseNode(BaseCommentNode):
	def __init__(self, *args, **kwargs):
		super(ThreadedCommentsBaseNode, self).__init__(*args, **kwargs)
		self.root_node = None
		self.comments_model = threaded_comments.get_model()

	def get_root_node(self, context):
		if self.root_node is None:
			ctype, object_pk = self.get_target_ctype_pk(context)
			self.root_node = self.comments_model.objects.get_root_comment(ctype, object_pk)
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
		header = threaded_comments.models.RootHeader.objects.get(content_type = ctype, object_id = object_pk)
		(discussion_attribute, created) = threaded_comments.models.UserDiscussionAttribute.objects.get_or_create(user = context['user'], discussion = header)
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
