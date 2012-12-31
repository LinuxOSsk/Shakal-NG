# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.decorators import available_attrs, method_decorator
from functools import wraps
from models import Page
from forms import WikiEditForm
from shakal.utils.generic import PreviewUpdateView
from shakal.utils import unique_slugify
import reversion


def show_page(request, slug = None, page = 1):
	if slug is None:
		wiki_page = get_object_or_404(Page, parent = None, page_type = 'h')
	else:
		wiki_page = get_object_or_404(Page, ~Q(page_type = 'i'), slug = slug)

	children = []

	template = "wiki/page.html"
	if wiki_page.page_type == 'h':
		if wiki_page.parent:
			template = "wiki/category.html"
			children = wiki_page.get_descendants().order_by('-modified')
		else:
			template = "wiki/home.html"
			children = wiki_page.get_children().filter(page_type = 'h')[:]
			for child in children:
				child.pages = child.get_descendants().order_by('-modified')
	else:
		children = wiki_page.get_children()

	context = {
		'page': wiki_page,
		'children': children,
		'pagenum': page,
		'tree': wiki_page.get_ancestors(),
	}

	return TemplateResponse(request, template, context)


def check_perms(view_func):
	def decorator(request, slug, *args, **kwargs):
		if not request.user.is_authenticated():
			return user_passes_test(lambda u: False)(view_func)(request)
		if request.user.is_staff and request.user.has_perm('admin:wiki_page_change'):
			return view_func(request, slug = slug, *args, **kwargs)
		else:
			wiki_page = get_object_or_404(Page, slug = slug)
			if wiki_page.page_type == 'p':
				return view_func(request, slug = slug, *args, **kwargs)
			else:
				return user_passes_test(lambda u: False)(view_func)(request)
	return decorator


class PageUpdateView(PreviewUpdateView):
	model = Page
	template_name = 'wiki/edit.html'
	form_class = WikiEditForm

	@method_decorator(check_perms)
	def dispatch(self, *args, **kwargs):
		with reversion.create_revision():
			response = super(PageUpdateView, self).dispatch(*args, **kwargs)
			reversion.set_user(args[0].user)
			return response

	def form_valid(self, form):
		page = form.save(commit = False)
		page.last_author = self.request.user
		return super(PageUpdateView, self).form_valid(form)

