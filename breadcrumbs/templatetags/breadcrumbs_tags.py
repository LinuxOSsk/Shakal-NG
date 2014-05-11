# -*- coding: utf-8 -*-
from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django_jinja import library
from jinja2 import contextfunction

from common_utils import process_template_args, process_template_kwargs


register = template.Library()
lib = library.Library()


class BreadcrumbNode(template.Node):
	def __init__(self, nodelist, params, urlparams):
		self.nodelist = nodelist
		self.params = params
		self.urlparams = urlparams

	def render(self, context):
		contents = self.nodelist.render(context)
		params = process_template_kwargs(self.params, context)
		reverse_args = process_template_args(self.urlparams, context)
		reverse_kwargs = process_template_kwargs(self.urlparams, context)

		url = params.get('absolute_url', False)
		if not url:
			url = params.get('url', False)
			if url:
				url = reverse(url, args = reverse_args, kwargs = reverse_kwargs)
		class_name = params.get('class', False)

		breadcrumb_context = {
			'contents': contents,
			'url': url,
			'class': class_name
		}

		if not 'breadcrumbs' in context:
			context['breadcrumbs'] = []
		context['breadcrumbs'].append(breadcrumb_context)
		return ''


@register.tag
def breadcrumb(parser, token):
	nodelist = parser.parse(('endbreadcrumb',))
	parser.delete_first_token()
	bits = token.split_contents()[1:]
	urlparams_pos = 0
	for bit in bits:
		urlparams_pos += 1
		if bit.find('url=') == 0:
			break
	params = bits[:urlparams_pos]
	urlparams = bits[urlparams_pos:]
	return BreadcrumbNode(nodelist, params, urlparams)


@contextfunction
@lib.global_function
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


@lib.global_function
def render_breadcrumbs(breadcrumbs):
	breadcrumbs.reverse()
	ctx = {'breadcrumbs': breadcrumbs}
	return render_to_string('breadcrumbs/breadcrumbs.html', ctx)


@register.inclusion_tag('breadcrumbs/breadcrumbs.html', takes_context=True)
def render_breadcrumbs(context):
	breadcrumbs = context.get('breadcrumbs', [])
	breadcrumbs.reverse()
	return {'breadcrumbs': breadcrumbs}
