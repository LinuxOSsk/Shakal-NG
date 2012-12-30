# -*- coding: utf-8 -*-

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from models import Page


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
			children = wiki_page.get_children()
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
