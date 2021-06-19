# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.conf import settings


DEFAULT_COOKIE_AGE = 3600 * 24 * 365 # rok


def set_cookie(response, cookie_name, cookie_value, cookie_age=None, **kwargs):
	if cookie_age is None:
		cookie_age = DEFAULT_COOKIE_AGE
	expires = datetime.utcnow() + timedelta(seconds=cookie_age)

	extra = {
		'domain': settings.SESSION_COOKIE_DOMAIN,
		'path': settings.SESSION_COOKIE_PATH,
		'secure': settings.SESSION_COOKIE_SECURE or None,
		'httponly': settings.SESSION_COOKIE_HTTPONLY or None,
	}
	extra.update(kwargs)

	response.set_cookie(
		cookie_name,
		cookie_value,
		max_age=None,
		expires=expires,
		**extra
	)
