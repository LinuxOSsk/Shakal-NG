from django.http import Http404
from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from paginator.paginator import Paginator
from shakal.paginator.settings import PAGINATOR_ITEMS_PER_PAGE
register = template.Library()

class AutoPaginateNode(template.Node):
	def __init__(self, objects, page, urlparams = [], url = None, inside = None, outside = None, items_per_page = PAGINATOR_ITEMS_PER_PAGE, raises_404 = None):
		self.objects = objects
		self.page = page
		self.items_per_page = items_per_page
		self.url = url
		self.urlparams = urlparams
		self.inside = inside
		self.outside = outside
		self.raises_404 = raises_404

	def render(self, context):
		urlparams = {}
		for param in self.urlparams:
			paramname = param
			paramvalue = ''
			try:
				pos = param.index('=')
				paramname = param[: pos]
				paramvalue = param[pos + 1:]
			except KeyError:
				pass
			paramvalue = template.resolve_variable(paramvalue, context)
			urlparams[paramname] = paramvalue

		objects = template.resolve_variable(self.objects, context)
		page = int(template.resolve_variable(self.page, context))
		url = template.resolve_variable(self.url, context)
		count = objects.count()
		items_per_page = int(template.resolve_variable(self.items_per_page, context))
		page_count = (count + items_per_page - 1) / items_per_page

		extra_args = {}
		if not self.inside is None:
			extra_args['inside'] = int(template.resolve_variable(self.inside, context))
		if not self.outside is None:
			extra_args['outside'] = int(template.resolve_variable(self.outside, context))
		if not self.raises_404 is None:
			extra_args['raises_404'] = bool(template.resolve_variable(self.raises_404, context))
		paginator = Paginator(page, page_count, url = url, urlparams = urlparams, **extra_args)

		context[self.objects] = objects[(page - 1) * items_per_page : (page) * items_per_page]
		context['paginator'] = paginator

		if paginator.raises_404:
			if paginator.current_page < 1 or paginator.current_page > paginator.page_count:
				context['request'].paginator_page_not_found = True
		return ''

@register.tag
def autopaginate(parser, token):
	split = token.split_contents()[1:]
	if len(split) < 2:
		raise template.TemplateSyntaxError("Variable required")
	objects = split[0]
	split = split[1:]
	page = split[0]
	split = split[1:]
	urlparams = []
	try:
		urlIdx = split.index('url')
		urlparams = split[urlIdx + 2:]
		split = split[0 : urlIdx + 2]
	except KeyError:
		pass
	params = dict(zip(split[::2], split[1::2]))
	return AutoPaginateNode(objects, page, urlparams, **params);

#class PaginatorNode(template.Node):
#	def __init__(self, template = 'paginator/paginator.html'):
#		self.template = template

#	def render(self, context):
#		return render_to_string(self.template, {}, context)


#@register.tag
#def paginator(parser, token):
#	return PaginatorNode()
@register.inclusion_tag('paginator/paginator.html', takes_context = True)
def paginator(context):
	paginator = context['paginator']
	return {
		'pages': paginator.pages,
		'current_page': paginator.current_page,
		'page_count': paginator.page_count,
		'next': paginator.next,
		'previous': paginator.previous,
		'paginated': len(paginator.pages) > 1,
		'url': paginator.url,
		'urlparams': paginator.urlparams,
	}

class ParserUrlNode(template.Node):
	def __init__(self, page):
		self.page = page

	def render(self, context):
		url = context['url']
		params = context['urlparams']
		params['page'] = int(template.resolve_variable(self.page, context))
		return reverse(url, kwargs = params)


@register.tag
def pager_url(parser, token):
	split = token.split_contents()
	if len(split) != 2:
		raise template.TemplateSyntaxError("Page number required")
	page_num = split[1]
	return ParserUrlNode(page_num)

