# -*- coding: utf-8 -*-
from django import template
from django.core.urlresolvers import reverse, NoReverseMatch


register = template.Library()


@register.inclusion_tag("paginator/paginator.html", takes_context=True)
def paginator(context, page_obj=None, page_kwarg='page'):
	page_obj = page_obj or context['page_obj']
	return {
		'page_obj': page_obj,
		'page_kwarg': page_kwarg,
		'resolver_match': context['request'].resolver_match,
		'request': context['request'],
	}


@register.simple_tag(takes_context=True)
def pager_url(context, page_num):
	request = context['request']
	resolver_match = context['resolver_match']
	page_kwarg = context['page_kwarg']
	kwargs = resolver_match.kwargs.copy()
	kwargs[page_kwarg] = page_num
	try:
		url_args = '?' + request.GET.urlencode() if request.GET else ''
		return reverse(resolver_match.view_name, args=resolver_match.args, kwargs=kwargs) + url_args
	except NoReverseMatch:
		get = request.GET.copy()
		get[page_kwarg] = page_num
		base_url = reverse(resolver_match.view_name, args=resolver_match.args, kwargs=resolver_match.kwargs)
		return base_url + '?' + get.urlencode()

