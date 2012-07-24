# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django import template
from shakal.utils import process_template_params

register = template.Library()

class BreadcrumbNode(template.Node):
	def __init__(self, nodelist, bits):
		self.nodelist = nodelist
		self.bits = bits

	def render(self, context):
		contents = self.nodelist.render(context)
		params = process_template_params(self.bits, context)

		url = params.get('url', False)
		if url:
			url = reverse(url)
		cls = params.get('class', False)

		breadcrumb_context = {
			'contents': contents,
			'url': url,
			'class': cls
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
	return BreadcrumbNode(nodelist, bits)


@register.inclusion_tag('breadcrumbs/breadcrumbs.html', takes_context = True)
def render_breadcrumbs(context):
	breadcrumbs = context.get('breadcrumbs', [])
	breadcrumbs.reverse()
	return {'breadcrumbs': breadcrumbs}

