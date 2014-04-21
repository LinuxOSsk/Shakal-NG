# -*- coding: utf-8 -*-
import hashlib
from django import template
from django.conf import settings
from django.utils.html import escape
from django_jinja import library


register = template.Library()
lib = library.Library()


GRAVATAR_URL_PREFIX = getattr(settings, "GRAVATAR_URL_PREFIX", "http://www.gravatar.com/")
GRAVATAR_DEFAULT_IMAGE = getattr(settings, "GRAVATAR_DEFAULT_IMAGE", "")
GRAVATAR_DEFAULT_SIZE = getattr(settings, "GRAVATAR_DEFAULT_IMAGE", 200)


@lib.global_function
@register.simple_tag
def gravatar_for_email(email, size=GRAVATAR_DEFAULT_SIZE):
	url = "%savatar/%s/?s=%s&default=%s" % (GRAVATAR_URL_PREFIX, hashlib.md5(bytes(email.encode('utf-8'))).hexdigest(), str(size), GRAVATAR_DEFAULT_IMAGE)
	return escape(url)


@lib.global_function
@register.simple_tag
def avatar_for_user(user, size=GRAVATAR_DEFAULT_SIZE):
	return gravatar_for_email(user.email, size)
