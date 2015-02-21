# -*- coding: utf-8 -*-
import os

import inspect
from django import template
from django.core.exceptions import ObjectDoesNotExist
from .middlewares.ThreadLocal import get_current_request


def process_template_args(rawparams, context = None):
	args = []
	for param in rawparams:
		pos = param.find('=')
		if (pos > 0):
			break
		if context is not None:
			param = template.resolve_variable(param, context)
		args.append(param)
	return args


def process_template_kwargs(rawparams, context = None):
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


def build_absolute_uri(path):
	request = get_current_request()
	if request:
		return request.build_absolute_uri(path)
	else:
		from django.conf import settings
		from django.contrib.sites.models import Site
		return 'http://' + Site.objects.get(pk = settings.SITE_ID) + path


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


def monkey_patch_safestring():
	from django.utils.safestring import SafeData
	SafeData.__html__ = lambda self: self

	from jinja2 import escape
	from django.forms import BaseForm, Media
	from django.forms.forms import BoundField
	from django.forms.formsets import BaseFormSet
	from django.forms.util import ErrorDict, ErrorList

	for cls in (BaseForm, Media, BoundField, BaseFormSet, ErrorDict, ErrorList):
		cls.__html__ = lambda self: escape(unicode(self))


monkey_patch_safestring()


def monkey_patch_jinja2_getattr():
	from jinja2.environment import Environment

	def env_getattr(self, obj, attribute):
		try:
			return Environment.old_getattr(self, obj, attribute)
		except ObjectDoesNotExist as exc:
			return self.undefined(obj=obj, name=attribute, hint=unicode(exc))

	def env_getitem(self, obj, attribute):
		try:
			return Environment.old_getitem(self, obj, attribute)
		except ObjectDoesNotExist as exc:
			return self.undefined(obj=obj, name=attribute, hint=unicode(exc))

	Environment.old_getattr = Environment.getattr
	Environment.old_getitem = Environment.getitem
	Environment.getattr = env_getattr
	Environment.getitem = env_getitem


monkey_patch_jinja2_getattr()
