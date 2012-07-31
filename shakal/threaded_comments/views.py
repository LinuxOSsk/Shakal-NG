# -*- coding: utf-8 -*-

from django.template.response import TemplateResponse
from shakal.threaded_comments.models import ThreadedComment
from shakal.threaded_comments import get_form

def reply_comment(request, parent):
	parent_comment = ThreadedComment.objects.get(pk = parent)
	content_object = parent_comment.content_object
	form = get_form()(content_object, parent_comment = parent_comment)

	model_meta = content_object.__class__._meta
	template_list = [
		"comments/{0}_{1}_new_form.html".format(*tuple(str(model_meta).split('.'))),
		"comments/{0}_new_form.html".format(model_meta.app_label),
		"comments/new_form.html",
	]
	return TemplateResponse(request, template_list, {'form': form, 'next': content_object.get_absolute_url() })

def post_comment(request):
	pass

def done_comment(request):
	pass
