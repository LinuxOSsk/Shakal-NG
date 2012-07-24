# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django import template
from shakal.utils import process_template_args, process_template_kwargs

register = template.Library()

class BreadcrumbNode(template.Node):
	def __init__(self, nodelist, required, optional):
		self.nodelist = nodelist
		self.required = required
		self.optional = optional

	def render(self, context):
		contents = self.nodelist.render(context)
		params = process_template_kwargs(self.required, context)
		reverse_args = process_template_args(self.optional, context)
		reverse_kwargs = process_template_kwargs(self.optional, context)

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
	optional_pos = 0
	for bit in bits:
		optional_pos += 1
		if bit.find('url=') == 0:
			break
	required = bits[:optional_pos]
	optional = bits[optional_pos:]
	return BreadcrumbNode(nodelist, required, optional)


@register.inclusion_tag('breadcrumbs/breadcrumbs.html', takes_context = True)
def render_breadcrumbs(context):
	breadcrumbs = context.get('breadcrumbs', [])
	breadcrumbs.reverse()
	return {'breadcrumbs': breadcrumbs}

