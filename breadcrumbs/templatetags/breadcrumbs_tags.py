# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django_jinja import library
from jinja2 import contextfunction


@contextfunction
@library.global_function
def breadcrumb(context, contents, *args, **kwargs):
	class_name = kwargs.pop('class', False)
	url = kwargs.pop('absolute_url', False)
	if not url:
		url = kwargs.pop('url', False)
		if url:
			url = reverse(url, args=args, kwargs=kwargs)

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
	return mark_safe(render_to_string('breadcrumbs/breadcrumbs.html', ctx))
