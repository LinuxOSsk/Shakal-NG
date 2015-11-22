# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import apps
from django.core.cache import caches


MODELS = [('article', 'article'), ('blog', 'post'), ('forum', 'topic'), ('news', 'news'), ('wiki', 'page')]
default_cache = caches['default']


def last_objects():
	objects_cache = default_cache.get('last_objects')
	if objects_cache is None:
		objects_cache = {}
		for app_label, model_name in MODELS:
			last = (apps.get_model(app_label, model_name).objects
				.order_by('-created')
				.values_list('created'))
			objects_cache[(app_label, model_name)] = last
		default_cache.set('last_objects', objects_cache)
	return objects_cache
