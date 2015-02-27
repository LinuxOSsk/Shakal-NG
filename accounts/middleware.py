# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import auth
from . import auth_remember_utils

from .accounts_settings import COOKIE_NAME


class AuthRememberMiddleware(object):
	def process_request(self, request):
		if request.user.is_authenticated():
			return

		token = request.COOKIES.get(COOKIE_NAME, None)
		if not token:
			return

		user = auth.authenticate(token_string=token, request=request)
		if user:
			auth.login(request, user)

	def process_response(self, request, response):
		auth_remember_token = getattr(request, '_auth_remember_token', None)

		if auth_remember_token is not None:
			if auth_remember_token:
				auth_remember_utils.set_cookie(response, auth_remember_token)
			else:
				auth_remember_utils.delete_cookie(response)
		return response
