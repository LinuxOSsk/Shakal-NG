# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from braces.views import PermissionRequiredMixin, LoginRequiredMixin
from django import http
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import capfirst
from django.template.response import TemplateResponse
from django.views.generic import DetailView
from django.views.generic.edit import FormView

from .forms import CommentForm
from .models import Comment
from .utils import update_comments_header
from common_utils import get_meta
from threaded_comments.models import RootHeader, UserDiscussionAttribute


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


class Reply(FormView):
	form_class = CommentForm
	parent = None

	def get_parent_comment(self):
		return get_object_or_404(Comment.objects.all(), pk=self.kwargs['parent'])

	def get_form_kwargs(self):
		kwargs = super(Reply, self).get_form_kwargs()
		kwargs['target_object'] = self.parent.content_object
		kwargs['parent_id'] = self.parent.id
		return kwargs

	def get_template_names(self):
		model = self.parent.content_object.__class__
		return (
			'comments/{0}_{1}_preview.html'.format(get_meta(model).app_label, get_meta(model).model_name),
			'comments/{0}_preview.html'.format(get_meta(model).app_label),
			'comments/preview.html',
		)

	def get_context_data(self, **kwargs):
		ctx = super(Reply, self).get_context_data(**kwargs)
		form = ctx['form']
		content_object = self.parent.content_object
		ctx.update({
			'next': self.request.POST.get('next', ''),
			'comment': form.get_comment_object(),
			'parent': self.parent if self.parent.parent_id else False,
			'content_object': content_object,
			'module_name': get_module_name(content_object),
			'module_url': get_module_url(content_object),
			'attachments': form.get_attachments(),
		})
		return ctx

	def dispatch(self, request, **kwargs):
		self.parent = self.get_parent_comment()
		form = self.get_form()
		if form.security_errors():
			return http.HttpResponseBadRequest()
		return super(Reply, self).dispatch(request, **kwargs)

	def form_valid(self, form):
		if not 'create' in self.request.POST:
			return self.render_to_response(self.get_context_data(form=form, valid=True))
		if self.parent.is_locked:
			return TemplateResponse(self.request, 'comments/error.html', self.get_context_data(form=form))

		comment = form.get_comment_object()
		comment.ip_address = self.request.META.get('REMOTE_ADDR', None)
		if self.request.user.is_authenticated():
			comment.user = self.request.user

		comment.save()
		form.move_attachments(comment)

		return http.HttpResponseRedirect(self.request.POST.get('next', '') + '#link_' + str(comment.pk))


class Admin(PermissionRequiredMixin, DetailView):
	model = Comment
	permission_required = 'threaded_comments.change_threaded_comment'

	def get(self, request, **kwargs):
		comment = self.get_object()

		delete = request.GET.get('delete', None)
		public = request.GET.get('public', None)
		lock = request.GET.get('lock', None)

		if delete is not None:
			comment.is_removed = bool(delete)
			comment.save()
		if public is not None:
			comment.is_public = bool(public)
			comment.save()
		if lock is not None:
			comment.get_descendants(include_self=True).update(is_locked=bool(lock))

		comment = Comment.objects.get(pk=comment.pk)
		update_comments_header(Comment, instance=comment)
		return HttpResponseRedirect(comment.content_object.get_absolute_url() + '#link_' + str(comment.pk))


class Watch(LoginRequiredMixin, DetailView):
	model = RootHeader

	def get(self, request, **kwargs):
		header = self.get_object()
		attributes = UserDiscussionAttribute.objects.get_or_create(user=request.user, discussion=header)
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


class Comments(DetailView):
	model = RootHeader
	template_name = 'comments/comments.html'

	def get_context_data(self, **kwargs):
		ctx = super(Comments, self).get_context_data(**kwargs)
		obj = ctx['object']
		ctx.update({
			'object': obj.content_object,
			'module_name': get_module_name(obj),
			'module_url': get_module_url(obj),
		})


class CommentDetail(DetailView):
	model = Comment
	template_name = 'comments/comments.html'

	def get_context_data(self, **kwargs):
		ctx = super(CommentDetail, self).get_context_data(**kwargs)
		comment = ctx['object']
		obj = comment.content_object
		ctx.update({
			'comment': comment,
			'object': obj,
			'module_name': get_module_name(obj),
			'module_url': get_module_url(obj),
			'single': False,
			'highlight': [comment.pk]
		})
		return ctx


class CommentDetailSingle(CommentDetail):
	def get_context_data(self, **kwargs):
		ctx = super(CommentDetailSingle, self).get_context_data(**kwargs)
		ctx['signle'] = True
		del ctx['highlight']
		if self.request.user.is_staff:
			ctx['can_display_deleted'] = True
		return ctx
