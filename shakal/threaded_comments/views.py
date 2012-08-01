# -*- coding: utf-8 -*-

from django import http
from django.contrib.comments.views.utils import next_redirect
from django.db import models
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
from shakal.threaded_comments.models import ThreadedComment
from shakal.threaded_comments import get_form


def reply_comment(request, parent):
	parent_comment = ThreadedComment.objects.get(pk = parent)
	content_object = parent_comment.content_object
	form = get_form()(content_object, logged = request.user.is_authenticated(), parent_comment = parent_comment)

	model_meta = content_object.__class__._meta
	template_list = [
		"comments/{0}_{1}_new_form.html".format(*tuple(str(model_meta).split('.'))),
		"comments/{0}_new_form.html".format(model_meta.app_label),
		"comments/new_form.html",
	]
	next = request.GET.get('next', content_object.get_absolute_url())
	return TemplateResponse(request, template_list, {'form': form, 'next': next })


@require_POST
def post_comment(request):
	data = request.POST.copy()
	if request.user.is_authenticated():
		data['email'] = request.user.email
		if request.user.get_full_name():
			data['name'] = request.user.get_full_name()
		else:
			data['name'] = request.user.username
	else:
		data['email'] = 'no@user.no'

	if not data['content_type'] or not data['object_pk'] or not data['parent_pk']:
		return http.HttpResponseBadRequest()

	model = models.get_model(*data['content_type'].split(".", 1))
	target = model._default_manager.get(pk = data['object_pk'])
	parent = ThreadedComment.objects.get(pk = data['parent_pk'])

	form = get_form()(target, logged = request.user.is_authenticated(), parent_comment = parent, data = data)
	if form.security_errors():
		return http.HttpResponseBadRequest()

	if form.errors or not 'create' in data:
		template_list = [
			"comments/{0}_{1}_preview.html".format(model._meta.app_label, model._meta.module_name),
			"comments/{0}_preview.html".format(model._meta.app_label),
			"comments/preview.html",
		]
		valid = not form.errors
		return TemplateResponse(request, template_list, {'form': form, 'next': data['next'], 'comment': form.get_comment_dict(), 'valid': valid })

	comment = form.get_comment_object()
	comment.ip_address = request.META.get("REMOTE_ADDR", None)
	if request.user.is_authenticated():
		comment.user = request.user

	comment.save()

	return next_redirect(data, data['next'], 'done-comment', c=comment._get_pk_val())


def done_comment(request):
	pass
