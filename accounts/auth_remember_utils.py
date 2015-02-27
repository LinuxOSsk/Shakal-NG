# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta

from .accounts_settings import COOKIE_AGE, COOKIE_NAME
from django.conf import settings


def create_token_string(user, token=None):
	from .models import RememberToken
	token_value = uuid.uuid4().hex
	token_hash = make_password(token_value)
	token = RememberToken(
		token_hash=token_hash,
		user=user
	)

	token.save()
	return '%d:%s' % (user.id, token_value)


def preset_cookie(request, token_string):
	if token_string:
		setattr(request, '_auth_remember_token', token_string)
	else:
		setattr(request, '_auth_remember_token', '')


def set_cookie(response, token):
	expires = datetime.utcnow() + timedelta(seconds=COOKIE_AGE)

	response.set_cookie(
		COOKIE_NAME,
		token,
		max_age=None,
		expires=expires,
		domain=settings.SESSION_COOKIE_DOMAIN,
		path=settings.SESSION_COOKIE_PATH,
		secure=settings.SESSION_COOKIE_SECURE or None,
		httponly=settings.SESSION_COOKIE_HTTPONLY or None
	)


def delete_cookie(response):
	response.delete_cookie(COOKIE_NAME)


def remember_user(response, user):
	token_string = create_token_string(user, None)
	set_cookie(response, token_string)
	return response
