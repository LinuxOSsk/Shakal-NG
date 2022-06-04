# -*- coding: utf-8 -*-
import os

import inspect

from web.middlewares.threadlocal import get_current_request


def iterify(items):
	try:
		iter(items)
		return items
	except TypeError:
		return [items]


def get_host_name():
	return 'linuxos.sk'


def build_absolute_uri(path):
	request = get_current_request()
	if request:
		return request.build_absolute_uri(path)
	else:
		return 'https://' + get_host_name() + path


def clean_dir(path, root_path):
	path = os.path.abspath(path)
	root_path = os.path.abspath(root_path)

	current_dir = path
	while len(os.path.split(current_dir)) and current_dir.startswith(root_path) and current_dir != root_path:
		try:
			os.rmdir(current_dir)
		except OSError:
			return
		current_dir = os.path.join(*os.path.split(current_dir)[:-1])


def get_meta(instance):
	return getattr(instance, "_meta")


def get_default_manager(obj):
	if inspect.isclass(obj):
		return getattr(obj, "_default_manager")
	else:
		return getattr(obj.__class__, "_default_manager")


def get_client_ip(request):
	return request.META.get('REMOTE_ADDR')
