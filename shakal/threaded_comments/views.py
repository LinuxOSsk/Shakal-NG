# -*- coding: utf-8 -*-

from django import http
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.comments.views.utils import next_redirect
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import capfirst
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
from django.utils.encoding import force_unicode
from shakal.threaded_comments.models import ThreadedComment, RootHeader, UserDiscussionAttribute, update_comments_header
from shakal.threaded_comments import get_form


def get_module_name(content_object):
	if hasattr(content_object, 'breadcrumb_label'):
		return capfirst(content_object.breadcrumb_label)
	else:
		return capfirst(content_object.__class__._meta.verbose_name_plural)


def get_module_url(content_object):
	if hasattr(content_object, 'get_list_url'):
		return content_object.get_list_url()
	else:
		return False


def reply_comment(request, parent):
	parent_comment = ThreadedComment.objects.get(pk = parent)
	content_object = parent_comment.content_object

	if parent_comment.parent_id:
		new_subject = parent_comment.subject
		if not new_subject.startswith(force_unicode('RE: ')):
			new_subject = force_unicode('RE: ') + new_subject
	else:
		new_subject = force_unicode('RE: ') + force_unicode(content_object)

	model_meta = content_object.__class__._meta
	template_list = [
		"comments/{0}_{1}_preview.html".format(*tuple(str(model_meta).split('.'))),
		"comments/{0}_preview.html".format(model_meta.app_label),
		"comments/preview.html",
	]
	next = request.GET.get('next', content_object.get_absolute_url())
	context = {
		'next': next,
		'parent': parent_comment if parent_comment.parent_id else False,
		'content_object': content_object,
		'module_name': get_module_name(content_object),
		'module_url': get_module_url(content_object),
	}

	if parent_comment.is_locked:
		return TemplateResponse(request, "comments/error.html", context)


	form = get_form()(content_object, logged = request.user.is_authenticated(), parent_comment = parent_comment, initial = {'subject': new_subject}, request = request)
	request.session['antispam'] = form.generate_antispam()
	form.set_antispam(request.session['antispam'])

	context["form"] = form
	context["attachments"] = form.get_attachments()

	return TemplateResponse(request, template_list, context)


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
	content_object = parent.content_object

	form = get_form()(target, logged = request.user.is_authenticated(), parent_comment = parent, data = data, files = request.FILES, request = request)

	if form.security_errors():
		return http.HttpResponseBadRequest()

	if form.errors or not 'create' in data or parent.is_locked:
		template_list = [
			"comments/{0}_{1}_preview.html".format(model._meta.app_label, model._meta.module_name),
			"comments/{0}_preview.html".format(model._meta.app_label),
			"comments/preview.html",
		]
		valid = not form.errors
		comment = form.get_comment_dict()
		if request.user.is_authenticated():
			comment['user'] = request.user
		context = {
			'next': data['next'],
			'comment': comment,
			'valid': valid,
			'parent': parent if parent.parent_id else False,
			'content_object': content_object,
			'module_name': get_module_name(content_object),
			'module_url': get_module_url(content_object),
			'form': form,
			'attachments': form.get_attachments(),
		}
		if parent.is_locked:
			del context['form']
			del context['attachments']
			return TemplateResponse(request, "comments/error.html", context)
		return TemplateResponse(request, template_list, context)

	comment = form.get_comment_object()
	comment.ip_address = request.META.get("REMOTE_ADDR", None)
	if request.user.is_authenticated():
		comment.user = request.user

	comment.save()
	form.move_attachments(comment)

	data['next'] = data['next'] + '#link_' + str(comment.pk)

	return next_redirect(request, data['next'], 'done-comment')


def done_comment(request):
	pass


def comments(request, header_id):
	header = get_object_or_404(RootHeader, id = header_id)
	object = header.content_object
	context = {
		'object': object,
		'module_name': get_module_name(object),
		'module_url': get_module_url(object),
	}
	return TemplateResponse(request, "comments/comments.html", context)


def comment(request, comment_id):
	comment = get_object_or_404(ThreadedComment, pk = comment_id)
	object = comment.content_object
	context = {
		'object': object,
		'module_name': get_module_name(object),
		'module_url': get_module_url(object),
		'highlight': [comment.pk]
	}
	return TemplateResponse(request, "comments/comments.html", context)


@login_required
def watch(request, header_id):
	header = get_object_or_404(RootHeader, id = header_id)
	attributes, created = UserDiscussionAttribute.objects.get_or_create(user = request.user, discussion = header)
	if 'watch' in request.GET:
		if request.GET['watch']:
			attributes.watch = 1
		else:
			attributes.watch = 0
	else:
		attributes.watch = 1
	attributes.save()
	obj = header.content_object
	return HttpResponseRedirect(obj.get_absolute_url())


@permission_required('threaded_comments.change_threaded_comment')
def lock(request, comment_id):
	if 'lock' in request.GET:
		if request.GET['lock']:
			lock = True
		else:
			lock = False
	else:
		lock = True
	comment = get_object_or_404(ThreadedComment, pk = comment_id)
	comment.get_descendants(include_self = True).update(is_locked = lock)
	comment = ThreadedComment.objects.get(pk = comment_id)
	update_comments_header(ThreadedComment, instance = comment)
	return HttpResponseRedirect(comment.content_object.get_absolute_url() + '#link_' + str(comment_id))
