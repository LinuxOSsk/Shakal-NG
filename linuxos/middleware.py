# -*- coding: utf-8 -*-
from django.conf import settings
from django.http.response import HttpResponsePermanentRedirect


HTTPS_VIEW_NAMES = {'account_login', 'admin:login'}


class HttpsRedirectMiddleware(object):
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		response = self.get_response(request)
		if response.status_code == 200 and request.method == 'GET' and request.resolver_match and request.resolver_match.view_name in HTTPS_VIEW_NAMES and request.scheme == 'http' and not settings.DEBUG:
			uri = request.build_absolute_uri(request.get_full_path())
			if uri.startswith('http://'):
				uri = 'https://' + uri[7:]
				return HttpResponsePermanentRedirect(uri)
		return response
