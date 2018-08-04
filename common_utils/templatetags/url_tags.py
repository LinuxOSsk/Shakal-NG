# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.encoding import force_text
from django_jinja import library
from jinja2 import contextfunction


def remove_dummy_parameters(get_data):
	get_data.pop('_dummy', None)
	get_data.pop('_visible_menu', None)


@library.global_function
@contextfunction
def link_add(context, url, **values):
	if not values:
		return url
	get_data = context['request'].GET.copy()
	remove_dummy_parameters(get_data)
	for k, v in values.items():
		get_data[k] = v
	separator = '&' if '?' in url else '?'
	return url + separator + get_data.urlencode('')


@library.global_function
@contextfunction
def link_remove(context, url, *keys):
	if not keys:
		return url
	get_data = context['request'].GET.copy()
	remove_dummy_parameters(get_data)
	for key in keys:
		if key in get_data:
			del get_data[key]
	encoded = get_data.urlencode('')
	if encoded:
		separator = '&' if '?' in url else '?'
		return url + separator + encoded
	else:
		return url


@library.global_function
@contextfunction
def current_link_add(context, **values):
	values = {key: force_text(value) for key, value in values.items()}
	return link_add(context, context['request'].path, **values)


@library.global_function
@contextfunction
def current_link_remove(context, *keys):
	return link_remove(context, context['request'].path, *keys)
