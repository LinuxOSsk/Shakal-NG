# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import inspect
from django import template

from .middlewares.ThreadLocal import get_current_request


def process_template_args(rawparams, context=None):
	args = []
	for param in rawparams:
		pos = param.find('=')
		if (pos > 0):
			break
		if context is not None:
			param = template.resolve_variable(param, context)
		args.append(param)
	return args


def process_template_kwargs(rawparams, context=None):
	kwargs = {}
	for param in rawparams:
		paramname = param
		paramvalue = ''
		pos = param.find('=')
		if (pos <= 0):
			continue
		paramname = param[:pos]
		paramvalue = param[pos + 1:]
		if context is not None:
			paramvalue = template.resolve_variable(paramvalue, context)
		kwargs[paramname] = paramvalue
	return kwargs


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
		return 'http://' + get_host_name() + path


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


def reload_model(obj):
	return get_default_manager(obj.__class__).get(pk=obj.pk)
