# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import QueryDict
from django.http.response import HttpResponseRedirect
from django.shortcuts import resolve_url


def build_query(query):
	q = QueryDict('', mutable=True)
	if isinstance(query, dict):
		items = query.items()
	else:
		items = query
	for key, value in items:
		q.appendlist(key, value)
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
