from django.core.urlresolvers import reverse
from django.template.base import Node
from django import template

register = template.Library()

class BreadcrumbNode(template.Node):
	def __init__(self, params, nodelist):
		template.Node.__init__(self)
		self.params = params
		self.nodelist = nodelist

	def render(self, context):
		contents = self.nodelist.render(context)
		url = False
		cls = False
		for param in self.params:
			#ret += template.Variable(param).resolve(context)
			if '=' in param:
				k, v = param.split('=', 1)
				if k == 'url':
					url = template.Variable(v).resolve(context)
				elif k == 'class':
					cls = template.Variable(v).resolve(context)
				else:
					print("Bad parameter: {0}".format(k))
			else:
				print("Bad parameter: {0}".format(param))
		if url:
			url = reverse(url)

		if not 'breadcrumbs' in context:
			context['breadcrumbs'] = []
		context['breadcrumbs'].append({'contents': contents, 'url': url, 'class': cls})
		return ''

@register.tag
def breadcrumb(parser, token):
	split = token.split_contents()[1:]
	nodelist = parser.parse(('endbreadcrumb',))
	parser.delete_first_token()
	return BreadcrumbNode(split, nodelist)


@register.inclusion_tag('breadcrumbs/breadcrumbs.html', takes_context = True)
def render_breadcrumbs(context):
	breadcrumbs = context['breadcrumbs']
	return {'breadcrumbs': breadcrumbs}

