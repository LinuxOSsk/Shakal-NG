# -*- coding: utf-8 -*-
import hashlib

from django.conf import settings
from django.utils.html import escape
from django_jinja import library

from accounts.utils import generated_avatar
from autoimagefield.utils import thumbnail


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
		avatar = thumbnail(user.avatar, size=(size, size), crop=True)
		if avatar:
			return avatar.url
	return gravatar_for_email(user.email, size)


@library.global_function
def prefetch_avatars_for_ip(*object_lists):
	icon_cache = {}

	for object_list in object_lists:
		for obj in object_list:
			ip = obj.ip_address
			if ip:
				if not ip in icon_cache:
					icon_cache[ip] = generated_avatar(ip)
				obj.ip_address_avatar = icon_cache[ip]

	return ''
