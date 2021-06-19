# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django_simple_paginator.utils import paginate_queryset
from reversion import revisions
from reversion.models import Version

from .forms import WikiEditForm
from .models import Page
from common_utils.generic import PreviewCreateView, PreviewUpdateView


class WikiBaseView(DetailView):
	object = None
	model = Page
	context_object_name = 'page'

	def get_children(self):
		raise NotImplementedError()

	def get_revision(self):
		history = self.kwargs.get('history', '')
		try:
			history = int(history)
		except ValueError:
			return None
		return get_object_or_404(self.get_history(), pk=history)

	def get_history(self):
		return (Version.objects
			.get_for_object(self.object)
			.select_related('revision', 'revision__user'))

	def get_context_data(self, **kwargs):
		ctx = super(WikiBaseView, self).get_context_data(**kwargs)
		children = self.get_children()
		revision = self.get_revision()
		history = self.get_history()
		ctx.update({
			'children': children,
			'revision': revision,
			'object_version': revision._object_version if revision else None, #pylint: disable=protected-access
			'history': history,
			'tree': self.object.get_ancestors(),
		})
		return ctx


class WikiHomeView(WikiBaseView):
	template_name = "wiki/home.html"

	def get_children(self):
		children = self.object.get_children().filter(page_type='h')[:]
		for child in children:
			child.pages = child.get_descendants().order_by('-updated')
		return children

	def get_object(self, **kwargs):
		return get_object_or_404(self.get_queryset(), parent=None, page_type='h')


class WikiDetailView(WikiBaseView):
	def get_template_names(self):
		if self.object.page_type == 'h':
			return ("wiki/category.html",)
		else:
			return ("wiki/page.html",)

	def get_object(self, **kwargs):
		return get_object_or_404(self.get_queryset(), ~Q(page_type='i'), slug=self.kwargs['slug'])

	def get_children(self):
		if self.object.page_type == 'h':
			return self.object.get_descendants().order_by('-updated')
		else:
			return self.object.get_children()

	def get_context_data(self, **kwargs):
		ctx = super(WikiDetailView, self).get_context_data(**kwargs)
		children = ctx['children']
		history = ctx['history']
		page = self.kwargs.get('page', None)
		if self.object.page_type == 'h':
			paginator, page, children, is_paginated = paginate_queryset(children, page or 1, 50)
		else:
			paginator, page, history, is_paginated = paginate_queryset(history, page or 1, 20)
		ctx.update({
			'children': children,
			'paginator': paginator,
			'page_obj': page,
			'is_paginated': is_paginated,
			'pagenum': page,
			'history': history,
		})
		return ctx


class PageEditMixin(UserPassesTestMixin):
	context_object_name = 'page'

	def test_func(self):
		request = self.request
		if not request.user.is_authenticated:
			return False

		wiki_page = get_object_or_404(Page, slug=self.kwargs['slug'])
		if request.user.is_staff and request.user.has_perm('admin:wiki_page_change'):
			return True

		if self.create:
			if wiki_page.page_type == 'p' or (wiki_page.page_type == 'h' and wiki_page.parent):
				return True
		else:
			if wiki_page.page_type == 'p':
				return True

		return False


class PageUpdateView(PageEditMixin, PreviewUpdateView):
	model = Page
	template_name = 'wiki/edit.html'
	form_class = WikiEditForm
	create = False

	def dispatch(self, *args, **kwargs):
		with revisions.create_revision():
			response = super(PageUpdateView, self).dispatch(*args, **kwargs)
			revisions.set_user(args[0].user)
		return response

	def form_valid(self, form):
		page = form.save(commit = False)
		page.last_author = self.request.user
		return super(PageUpdateView, self).form_valid(form)


class PageCreateView(PageEditMixin, PreviewCreateView):
	model = Page
	template_name = 'wiki/create.html'
	form_class = WikiEditForm
	extra_context = {}
	create = True

	def dispatch(self, *args, **kwargs):
		self.extra_context = {'slug': kwargs['slug'], 'page': get_object_or_404(Page, slug=kwargs['slug'])}
		with revisions.create_revision():
			response = super(PageCreateView, self).dispatch(*args, **kwargs)
			revisions.set_user(args[0].user)
		return response

	def get_context_data(self, **kwargs):
		context = super(PageCreateView, self).get_context_data(**kwargs)
		context.update(self.extra_context)
		return context

	def form_valid(self, form):
		page = form.save(commit = False)
		page.last_author = self.request.user
		page.parent = self.extra_context['page']
		return super(PageCreateView, self).form_valid(form)
