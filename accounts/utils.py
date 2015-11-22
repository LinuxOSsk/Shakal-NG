# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bisect import bisect_left
from django.apps import apps
from django.core.cache import caches

from common_utils import get_meta


MODELS = [
	'article.article',
	'blog.post',
	'forum.topic',
	'news.news',
	'wiki.page',
]

default_cache = caches['default']


def last_objects():
	objects_cache = default_cache.get('last_objects')
	if objects_cache is None:
		objects_cache = {}
		for model in MODELS:
			last = (apps.get_model(model).objects
				.order_by('-created')
				.values_list('created', flat=True)[:99])
			objects_cache[model] = list(reversed(last))
		default_cache.set('last_objects', objects_cache)
	return objects_cache


def clear_last_objects_cache(sender, **kwargs):
	opts = get_meta(sender)
	if (opts.app_label, opts.model_name) not in MODELS:
		return
	default_cache.delete('last_objects')


def count_new(last_display_time):
	counts = {}
	for model, dates in last_objects().iteritems():
		if model in last_display_time:
			counts[model] = len(dates) - bisect_left(dates, last_display_time[model])
		else:
			counts[model] = None
	return counts
