# -*- coding: utf-8 -*-
from allauth.account.auth_backends import AuthenticationBackend as CoreAuthenticationBackend
from django.contrib.auth import get_user_model

from .models import RememberToken


class AuthRememberBackend(object):
	def authenticate(self, request, token_string=None): #pylint: disable=unused-argument
		token = RememberToken.objects.get_by_string(token_string)
		if not token:
			return

		return token.user

	def get_user(self, user_id):
		try:
			return get_user_model().objects.get(pk=user_id)
		except get_user_model().DoesNotExist:
			return None


class AuthenticationBackend(CoreAuthenticationBackend):
	def _authenticate_by_username(self, **credentials):
		username = credentials.get('username')
		password = credentials.get('password')

		User = get_user_model()

		if username is None or password is None:
			return None
		try:
			try:
				user = User.objects.get(username__iexact=username)
			except User.MultipleObjectsReturned:
				user = User.objects.get(username=username)
			if user.check_password(password):
				return user
		except User.DoesNotExist:
			return None
