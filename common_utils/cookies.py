# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.conf import settings


def set_cookie(response, cookie_name, cookie_value, cookie_age):
	expires = datetime.utcnow() + timedelta(seconds=cookie_age)

	response.set_cookie(
		cookie_name,
		cookie_value,
		max_age=None,
		expires=expires,
		domain=settings.SESSION_COOKIE_DOMAIN,
		path=settings.SESSION_COOKIE_PATH,
		secure=settings.SESSION_COOKIE_SECURE or None,
		httponly=settings.SESSION_COOKIE_HTTPONLY or None
	)
