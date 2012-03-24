from django.conf import settings
from django.contrib.comments.templatetags.comments import BaseCommentNode, CommentListNode
from django.template.loader import render_to_string
from django.template.base import Node
from django import template
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_unicode
from shakal import threaded_comments

register = template.Library()

class ThreadedCommentsBaseNode(BaseCommentNode):
	def __init__(self, ctype=None, object_pk_expr=None, object_expr=None, as_varname=None, comment=None):
		super(ThreadedCommentsBaseNode, self).__init__(ctype=ctype, object_pk_expr=object_pk_expr, object_expr=object_expr, as_varname=as_varname, comment=comment)
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

		querySet = self.comments_model.comment_objects.filter(
			content_type = ctype,
			object_pk = smart_unicode(object_pk),
			site__pk = settings.SITE_ID
		)
		#querySet = super(ThreadedCommentsBaseNode, self).get_query_set(context).filter(content_type = ctype, object_pk = object_pk)
		querySet = querySet.order_by('lft').select_related('user')
		return querySet

	def get_query_set(self, context):
		ctype, object_pk = self.get_target_ctype_pk(context)
		querySet = self.get_comments_query_set(context)
		if not querySet.has_root_item():
			rootNode = self.comments_model.objects.get_root_comment(ctype, smart_unicode(object_pk))
			querySet.set_root_item(rootNode)
		return querySet


class ThreadedCommentsListNode(ThreadedCommentsBaseNode):
	def get_query_set(self, context):
		querySet = super(ThreadedCommentsListNode, self).get_query_set(context)
		return querySet

	def render(self, context):
		query_set = self.get_query_set(context)
		context[self.as_varname] = query_set
		return ''


class ThreadedCommentsFormNode(ThreadedCommentsBaseNode):
	def get_form(self, context):
		ctype, object_pk = self.get_target_ctype_pk(context)
		key = str(ctype)+'_'+str(object_pk)
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


@register.simple_tag
def render_threaded_comments_toplevel(target):
	modelClass = target.__class__
	templates = [
		"comments/{0}_{1}_comments_toplevel.html".format(*str(modelClass._meta).split('.')),
		"comments/{0}_comments_toplevel.html".format(modelClass._meta.app_label),
		"comments/comments_toplevel.html".format(modelClass._meta.app_label),
	]
	return mark_safe(render_to_string(templates, {"target": target}))

