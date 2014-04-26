# -*- coding: utf-8 -*-

from django import template
from django.core.urlresolvers import reverse, NoReverseMatch
from django.template.loader import render_to_string
from django.utils.http import urlencode
from paginator.paginator import Paginator
from paginator.settings import PAGINATOR_ITEMS_PER_PAGE
from django_jinja import library
from jinja2 import contextfunction

register = template.Library()
lib = library.Library()

def process_params(rawparams, context = None):
	"""
	Spracovanie parametrov vo formáte názov, alebo  názov=hodnota do dictionary
	spolu s resolvovaním hodnoty podľa kontextu za predpokladu, že context je
	nastavený. Ak je parameter bez hodnoty dosadí sa ako hodnota parametru True.
	"""
	params = {}
	for param in rawparams:
		paramname = param
		paramvalue = ''
		try:
			pos = param.index('=')
			paramname = param[: pos]
			paramvalue = param[pos + 1:]
			if context is not None:
				paramvalue = template.resolve_variable(paramvalue, context)
		except KeyError:
			paramvalue = True
			pass
		params[paramname] = paramvalue
	return params

class AutoPaginateNode(template.Node):
	"""
	Tag pre automatické stránkovanie QuerySet-u.

	Použitie:
	{% autopaginate queryset aktualna_stranka param=val ... }

	Podporované parametre sú:
	:param items_per_page: Počet objektov na stránke.
	:param inside: Počet stránok vpred a vzad od aktuálnej stránky.
	:param outside: Počet stránok od začiatku a konca zoznamu stránok.
	:param raises_404: Nastaví paginator_page_not_found na True. Ak je povolený
	middleware paginator.middleware.PaginatorMiddleware vyvolá toto nastavenie
	výnimku 404
	"""
	def __init__(self, objects, page, params):
		"""
		:param objects: QuerySet, na ktorý sa aplikuje stránkovač
		:param page: Číslo aktuálnej stránky alebo názov kontextovej premennej.
		:param raises_404: Ak nebudú vrátené žiadne položky vyvolá chybu 404.
		:param params: Parametre vo formáte názov=hodnota
		"""
		self.objects = objects
		self.page = page
		self.params = params
		self.items_per_page = PAGINATOR_ITEMS_PER_PAGE
		self.inside = None
		self.outside = None
		self.raises_404 = None

	def render(self, context):
		params = process_params(self.params)
		for param in params:
			setattr(self, param, params[param])

		objects = template.resolve_variable(self.objects, context)
		try:
			page = int(self.page)
		except ValueError:
			page = int(template.resolve_variable(self.page, context))
		count = objects.count()
		if (isinstance(self.items_per_page, int)):
			items_per_page = self.items_per_page
		else:
			items_per_page = int(template.resolve_variable(self.items_per_page, context))
		page_count = (count + items_per_page - 1) / items_per_page

		extra_args = {}
		if not self.inside is None:
			extra_args['inside'] = int(template.resolve_variable(self.inside, context))
		if not self.outside is None:
			extra_args['outside'] = int(template.resolve_variable(self.outside, context))
		if not self.raises_404 is None:
			extra_args['raises_404'] = bool(template.resolve_variable(self.raises_404, context))
		paginator = Paginator(page, page_count, **extra_args)

		context[self.objects] = objects[(page - 1) * items_per_page : (page) * items_per_page]
		context['paginator'] = paginator

		# Nastavenie kontextu pre paginator.middleware.Paginatormiddleware
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
	page = split[1]
	params = []
	if len(split) > 2:
		params = split[2:]

	return AutoPaginateNode(objects, page, params);


class PaginatorNode(template.Node):
	"""
	Zobrazenie stránkovača. Pred volaním tohto tagu je potrebné použiť tag
	autopaginate.

	Použitie tagu:
	{% paginator reverzné_url názov=parameter ... %}
	"""
	def __init__(self, url, urlparams):
		self.url = url
		self.urlparams = urlparams

	def render(self, context):
		urlparams = process_params(self.urlparams, context)
		paginator = context['paginator']

		if 'request' in context:
			request = context['request']
		else:
			request = None

		extra_context = {
			'pages': paginator.pages,
			'current_page': paginator.current_page,
			'page_count': paginator.page_count,
			'next': paginator.next,
			'previous': paginator.previous,
			'paginated': len(paginator.pages) > 1,
			'url': self.url,
			'urlparams': urlparams,
			'request': request,
		}
		return render_to_string('paginator/paginator.html', extra_context, context)


@register.tag
def paginator(parser, token):
	split = token.split_contents()[1:]
	url = split[0]
	urlparams = []
	if len(split) > 1:
		urlparams = split[1:]
	return PaginatorNode(url, urlparams)


class ParserUrlNode(template.Node):
	"""
	Renderovanie reverzného URL stránkovača. Tento tag je platný len v šablóne
	stránkovača.
	"""
	def __init__(self, page):
		self.page = page

	def render(self, context):
		url = context['url']
		params = context['urlparams']
		params['page'] = int(template.resolve_variable(self.page, context))
		try:
			return reverse(url, kwargs = params)
		# Ak sa nenájde reverzné URL použijú sa GET parametre
		except NoReverseMatch:
			query_string = ''
			if 'query_string' in context:
				query_string = context['query_string']
			elif 'request' in context:
				request = context['request']
				get = request.GET.copy()
				if 'page' in get:
					del get['page']
				get_list = []
				for item in get:
					val = get.getlist(item)
					if val is not None:
						for part in val:
							get_list.append((item, part))
					else:
						val = get.get(item)
						get_list.append((item, val))
				query_string = urlencode(get_list)
				context['query_string'] = query_string
			if len(query_string):
				query_string += u'&'
			query_string += urlencode({'page': params['page']})
			del(params['page'])
			return reverse(url, kwargs = params) + u'?' + query_string


@register.tag
def pager_url(parser, token):
	split = token.split_contents()
	if len(split) != 2:
		raise template.TemplateSyntaxError("Page number required")
	page_num = split[1]
	return ParserUrlNode(page_num)

