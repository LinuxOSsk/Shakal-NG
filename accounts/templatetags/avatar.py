# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib

from django.conf import settings
from django.utils.html import escape
from django_jinja import library


GRAVATAR_URL_PREFIX = getattr(settings, "GRAVATAR_URL_PREFIX", "//www.gravatar.com/")
GRAVATAR_DEFAULT_IMAGE = getattr(settings, "GRAVATAR_DEFAULT_IMAGE", "")
GRAVATAR_DEFAULT_SIZE = getattr(settings, "GRAVATAR_DEFAULT_IMAGE", 200)


@library.global_function
def gravatar_for_email(email, size=GRAVATAR_DEFAULT_SIZE):
	url = "%savatar/%s/?s=%s&default=%s" % (GRAVATAR_URL_PREFIX, hashlib.md5(bytes(email.encode('utf-8'))).hexdigest(), str(size), GRAVATAR_DEFAULT_IMAGE)
	return escape(url)


@library.global_function
def avatar_for_user(user, size=GRAVATAR_DEFAULT_SIZE):
	if user.avatar:
		avatar = getattr(user, 'avatar_' + str(size))
		if avatar:
			return avatar.url
	return gravatar_for_email(user.email, size)
