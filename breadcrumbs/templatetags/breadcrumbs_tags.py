# -*- coding: utf-8 -*-
from django.shortcuts import resolve_url
from django.template.loader import render_to_string
from django_jinja import library
from jinja2 import pass_context


@pass_context
@library.global_function
def breadcrumb(context, contents, *args, **kwargs):
	class_name = kwargs.pop('class', False)
	url = kwargs.pop('url', False)
	if url is not False:
		url = resolve_url(url, *args, **kwargs)

	breadcrumb_context = {
		'contents': contents,
		'url': url,
		'class': class_name
	}
	context['breadcrumbs'].append(breadcrumb_context)
	return ''


@library.global_function
def render_breadcrumbs(breadcrumbs):
	breadcrumbs.reverse()
	ctx = {'breadcrumbs': breadcrumbs}
	return render_to_string('breadcrumbs/breadcrumbs.html', ctx)
