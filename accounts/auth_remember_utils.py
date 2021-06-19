# -*- coding: utf-8 -*-
import secrets

from django.contrib import auth as django_auth

from .accounts_settings import COOKIE_AGE, COOKIE_NAME
from common_utils.cookies import set_cookie


def create_token_string(user, token=None):
	from .models import RememberToken
	token_hash = secrets.token_urlsafe(64)
	token = RememberToken(
		token_hash=token_hash,
		user=user
	)

	token.save()
	return '%d:%s' % (user.id, token_hash)


def preset_cookie(request, token_string):
	if token_string:
		setattr(request, '_auth_remember_token', token_string)
	else:
		setattr(request, '_auth_remember_token', '')


def delete_cookie(response):
	response.delete_cookie(COOKIE_NAME)


def remember_user(response, user):
	token_string = create_token_string(user, None)
	set_cookie(response, COOKIE_NAME, token_string, COOKIE_AGE, httponly=True)
	return response


def authenticate_user(request):
	token = request.COOKIES.get(COOKIE_NAME, None)
	if token is None:
		return False

	user = django_auth.authenticate(token_string=token, request=request)
	if user:
		django_auth.login(request, user)
	return user
