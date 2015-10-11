# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
try:
	from threading import local
except ImportError:
	from django.utils._threading_local import local


_thread_locals = local()


def get_current_request():
	return getattr(_thread_locals, "request", None)


def get_current_user():
	request = get_current_request()
	if request:
		return getattr(request, "user", None)


class ThreadLocalMiddleware(object):
	def process_request(self, request):
		_thread_locals.request = request
		setattr(request, 'request_time', timezone.localtime(timezone.now()))
