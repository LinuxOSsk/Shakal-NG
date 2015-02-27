# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model

from .models import RememberToken


class AuthRememberBackend(object):
	def authenticate(self, token_string, request): #pylint: disable=unused-argument
		token = RememberToken.objects.get_by_string(token_string)
		if not token:
			return

		return token.user

	def get_user(self, user_id):
		try:
			return get_user_model().objects.get(pk=user_id)
		except get_user_model().DoesNotExist:
			return None
