# -*- coding: utf-8 -*-
from django import http
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import capfirst
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import ngettext
from django.views.generic import DetailView, View
from django.views.generic.edit import FormView

from .forms import CommentForm
from .models import Comment
from .utils import get_requested_time, update_comments_header
from comments.models import RootHeader, UserDiscussionAttribute
from comments.templatetags.comments_tags import add_discussion_attributes
from common_utils import get_meta
from common_utils.url_utils import link_add_query


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


class Reply(UserPassesTestMixin, FormView):
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
		comment = form.get_comment_object()
		if comment is not None and self.request.user.is_authenticated:
			comment.user = self.request.user
		ctx.update({
			'next': self.request.POST.get('next', self.request.GET.get('next', content_object.get_absolute_url())),
			'time': self.request.POST.get('time', get_requested_time(self.request, as_timestamp=True)),
			'comment': comment,
			'parent': self.parent if self.parent.parent_id else False,
			'content_object': content_object,
			'module_name': get_module_name(content_object),
			'module_url': get_module_url(content_object),
			'attachments': form.get_attachments(),
		})
		return ctx

	def dispatch(self, request, **kwargs):
		self.parent = self.get_parent_comment()
		return super(Reply, self).dispatch(request, **kwargs)

	def form_valid(self, form):
		if form.security_errors():
			return http.HttpResponseBadRequest()
		if not 'create' in self.request.POST:
			return self.render_to_response(self.get_context_data(form=form, valid=True))
		if self.parent.is_locked:
			return TemplateResponse(self.request, 'comments/error.html', self.get_context_data(form=form))

		comment = form.get_comment_object()
		if self.request.user.is_authenticated:
			comment.user = self.request.user

		comment.save()
		form.move_attachments(comment)

		next_url = self.request.POST.get('next', '')
		if self.request.POST.get('time'):
			next_url = link_add_query(next_url, time=self.request.POST['time'])
		return http.HttpResponseRedirect(next_url + '#link_' + str(comment.pk))

	def test_func(self):
		return settings.ANONYMOUS_COMMENTS or self.request.user.is_authenticated


class Admin(PermissionRequiredMixin, DetailView):
	model = Comment
	permission_required = 'comments.change_threaded_comment'

	def get(self, request, *args, **kwargs):
		return http.HttpResponseBadRequest()

	def post(self, request, **kwargs):
		comment = self.get_object()

		delete = request.POST.get('delete', None)
		public = request.POST.get('public', None)
		lock = request.POST.get('lock', None)

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

	def get(self, request, *args, **kwargs):
		return http.HttpResponseBadRequest()

	def post(self, request, **kwargs):
		header = self.get_object()
		attributes = UserDiscussionAttribute.objects.get_or_create(user=request.user, discussion=header)[0]
		if 'watch' in request.POST:
			if request.POST['watch']:
				attributes.watch = 1
			else:
				attributes.watch = 0
		else:
			attributes.watch = 1
		attributes.save()
		if 'next' in request.POST:
			return HttpResponseRedirect(request.POST['next'])
		else:
			obj = header.content_object
			return HttpResponseRedirect(obj.get_absolute_url())


class Forget(LoginRequiredMixin, DetailView):
	model = RootHeader

	def get(self, request, **kwargs):
		header = self.get_object()
		UserDiscussionAttribute.objects.filter(user=request.user, discussion=header).delete()
		if 'next' in request.GET:
			return HttpResponseRedirect(request.GET['next'])
		else:
			return HttpResponseRedirect(reverse('home'))


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
		return ctx


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
			'single': True,
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


class CommentCountImage(View):
	def get_comment_count(self):
		ctype = get_object_or_404(ContentType, pk=self.kwargs['ctype'])
		instance = get_object_or_404(ctype.model_class(), pk=self.kwargs['pk'])
		add_discussion_attributes({}, [instance])
		return instance.comment_count

	def get(self, request, **kwargs):
		from PIL import Image, ImageDraw

		size = (160, 10)
		im = Image.new('RGB', size, color=(255, 255, 255))
		draw = ImageDraw.Draw(im)


		comment_count = self.get_comment_count()
		text = ngettext('%(num)s comment', '%(num)s comments', comment_count) % {'num': comment_count}
		draw.text((0, 0), text, fill=(0, 0, 255))
		del draw

		response = HttpResponse(content_type='image/png')
		im.save(response, 'PNG')
		return response
