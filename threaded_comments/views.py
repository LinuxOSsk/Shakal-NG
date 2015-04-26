# -*- coding: utf-8 -*-
from django import http
from django.contrib.auth.decorators import login_required, permission_required
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import capfirst
from django.template.response import TemplateResponse
from django.utils.encoding import force_unicode
from django.views.decorators.http import require_POST

from common_utils import get_default_manager, get_meta
from threaded_comments import get_form, signals
from threaded_comments.models import Comment, CommentFlag, RootHeader, UserDiscussionAttribute, update_comments_header


def get_module_name(content_object):
	if hasattr(content_object, 'breadcrumb_label'):
		return capfirst(content_object.breadcrumb_label)
	else:
		return capfirst(get_meta(content_object).verbose_name_plural)


def get_module_url(content_object):
	if hasattr(content_object, 'get_list_url'):
		return content_object.get_list_url()
	else:
		return False


def reply_comment(request, parent):
	parent_comment = get_object_or_404(Comment.all_comments, pk = parent)
	content_object = parent_comment.content_object

	if parent_comment.parent_id:
		new_subject = parent_comment.subject
		if not new_subject.startswith(force_unicode('RE: ')):
			new_subject = force_unicode('RE: ') + new_subject
	else:
		new_subject = force_unicode('RE: ') + force_unicode(content_object)

	model_meta = get_meta(content_object)
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

	form = get_form()(content_object, logged = request.user.is_authenticated(), parent_comment = parent_comment, initial = {'subject': new_subject})

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

	if not data['content_type'] or not data['object_id'] or not data['parent_pk']:
		return http.HttpResponseBadRequest()

	model = models.get_model(*data['content_type'].split(".", 1))
	target = get_default_manager(model).get(pk = data['object_id'])
	parent = Comment.all_comments.get(pk = data['parent_pk'])
	content_object = parent.content_object

	form = get_form()(target, logged = request.user.is_authenticated(), parent_comment = parent, data = data, files = request.FILES)

	if form.security_errors():
		return http.HttpResponseBadRequest()

	if form.errors or not 'create' in data or parent.is_locked:
		template_list = [
			"comments/{0}_{1}_preview.html".format(get_meta(model).app_label, get_meta(model).model_name),
			"comments/{0}_preview.html".format(get_meta(model).app_label),
			"comments/preview.html",
		]
		valid = not form.errors
		comment = form.get_comment()
		if request.user.is_authenticated():
			comment.user = request.user
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
	return HttpResponseRedirect(data['next'])


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


def comment(request, comment_id, single = True):
	comment = get_object_or_404(Comment, pk = comment_id)
	object = comment.content_object
	context = {
		'comment': comment,
		'object': object,
		'module_name': get_module_name(object),
		'module_url': get_module_url(object),
		'single': single,
	}
	if not single:
		context['highlight'] = [comment.pk]
	else:
		if request.user.is_staff:
			context['can_display_deleted'] = True
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
def admin(request, comment_id):
	delete = request.GET.get('delete', None)
	public = request.GET.get('public', None)
	lock = request.GET.get('lock', None)
	comment = get_object_or_404(Comment, pk = comment_id)
	if delete is not None:
		comment.is_removed = bool(delete)
		comment.save()
	if public is not None:
		comment.is_public = bool(public)
		comment.save()
	if lock is not None:
		comment.get_descendants(include_self = True).update(is_locked = bool(lock))
	comment = Comment.all_comments.get(pk = comment_id)
	update_comments_header(Comment, instance = comment)
	return HttpResponseRedirect(comment.content_object.get_absolute_url() + '#link_' + str(comment_id))


def perform_action_view(action, template, request, comment_id, next):
	comment = get_object_or_404(Comment, pk = comment_id)
	if request.method == 'POST':
		action(request, comment)
		return HttpResponseRedirect(next)
	else:
		return TemplateResponse(request, template, {'comment': comment, 'next': next})


@login_required
def flag(request, comment_id, next):
	return perform_action_view(perform_flag, "comments/flag.html", request, comment_id, next)


@permission_required("comments.can_moderate")
def delete(request, comment_id, next):
	return perform_action_view(perform_delete, "comments/delete.html", request, comment_id, next)


@permission_required("comments.can_moderate")
def approve(request, comment_id, next):
	return perform_action_view(perform_approve, "comments/approve.html", request, comment_id, next)


def perform_flag_action(request, comment, comment_flag, action = None):
	flag, created = CommentFlag.objects.get_or_create(
		comment = comment,
		user = request.user,
		flag = comment_flag
	)
	if action:
		action(comment)
	signals.comment_was_flagged.send(
		sender = comment.__class__,
		comment = comment,
		flag = flag,
		created = created,
		request = request
	)


def perform_flag(request, comment):
	perform_flag_action(request, comment, CommentFlag.SUGGEST_REMOVAL)


def perform_delete(request, comment):
	def action(comment):
		comment.is_removed = True
		comment.save()
	perform_flag_action(request, comment, CommentFlag.MODERATOR_DELETION, action)


def perform_approve(request, comment):
	def action(comment):
		comment.is_removed = False
		comment.is_public = True
		comment.save()
	perform_flag_action(request, comment, CommentFlag.MODERATOR_APPROVAL, action)
