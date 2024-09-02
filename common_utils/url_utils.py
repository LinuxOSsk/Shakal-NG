# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlparse, urlunparse

from django.http import QueryDict
from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import resolve_url
from django.utils.encoding import force_str
from django.utils.http import url_has_allowed_host_and_scheme


logger = logging.getLogger(__name__)


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


def check_redirect_url(redirect_to, request):
	url_is_safe = url_has_allowed_host_and_scheme(
		url=redirect_to,
		allowed_hosts=[request.get_host()],
		require_https=request.is_secure(),
	)
	if not url_is_safe:
		logger.warning("Unsafe redirect to: %s", redirect_to)
		raise Http404("Unsafe redirect to: %s" % redirect_to)
