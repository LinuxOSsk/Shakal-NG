# -*- coding: utf-8 -*-
import urllib
from django import template
from django.conf import settings
from django.utils.hashcompat import md5_constructor
from django.utils.html import escape


register = template.Library()


GRAVATAR_URL_PREFIX = getattr(settings, "GRAVATAR_URL_PREFIX", "http://www.gravatar.com/")
GRAVATAR_DEFAULT_IMAGE = getattr(settings, "GRAVATAR_DEFAULT_IMAGE", "")
GRAVATAR_DEFAULT_SIZE = getattr(settings, "GRAVATAR_DEFAULT_IMAGE", 200)


@register.simple_tag
def gravatar_for_email(email, size = GRAVATAR_DEFAULT_SIZE):
	url = "%savatar/%s/?" % (GRAVATAR_URL_PREFIX, md5_constructor(email).hexdigest())
	url += urllib.urlencode({"s": str(size), "default": GRAVATAR_DEFAULT_IMAGE})
	return escape(url)


@register.simple_tag
def avatar_for_user(user, size = GRAVATAR_DEFAULT_SIZE):
	return gravatar_for_email(user.email, size)
