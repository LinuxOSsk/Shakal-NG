# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
from django.contrib.auth.hashers import make_password

from .accounts_settings import COOKIE_AGE, COOKIE_NAME
from common_utils.cookies import set_cookie


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


def delete_cookie(response):
	response.delete_cookie(COOKIE_NAME)


def remember_user(response, user):
	token_string = create_token_string(user, None)
	set_cookie(response, COOKIE_NAME, token_string, COOKIE_AGE)
	return response
