# -*- coding: utf-8 -*-
from urllib.parse import urlparse, urlunparse

from django.http import QueryDict
from django.http.response import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.utils.encoding import force_str


def build_query(query):
	q = QueryDict('', mutable=True)
	if isinstance(query, dict):
		items = query.items()
	else:
		items = query
	for key, value in items:
		q.appendlist(key, force_str(value))
	return q.urlencode()


def build_url(url, args=None, kwargs=None, query=None):
	args = args or []
	kwargs = kwargs or {}
	query = query or {}
	path = resolve_url(url, *args, **kwargs)
	query_string = build_query(query)
	if query_string:
		if '?' in path:
			return path + '&' + query_string
		else:
			return path + '?' + query_string
	else:
		return path


def redirect_url(*args, **kwargs):
	return HttpResponseRedirect(build_url(*args, **kwargs))


def link_add_query(url, **values):
	if not values:
		return url
	parsed = list(urlparse(url))

	query_string_position = 4
	q = QueryDict(parsed[query_string_position], mutable=True)
	parsed[query_string_position] = ''
	url = urlunparse(parsed)

	for key, value in values.items():
		q[key] = value
	return '%s?%s' % (url, q.urlencode(''))
