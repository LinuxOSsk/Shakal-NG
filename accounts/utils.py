# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bisect import bisect_left
from django.apps import apps
from django.core.cache import caches
from django.utils import timezone
from django.utils.dateparse import parse_datetime

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
				.values_list('pk', 'created')[:99])
			objects_cache[model] = list(reversed(last))
		default_cache.set('last_objects', objects_cache, 60)
	return objects_cache


def clear_last_objects_cache(sender, **kwargs):
	opts = get_meta(sender)
	if '.'.join((opts.app_label, opts.model_name)) not in MODELS:
		return
	default_cache.delete('last_objects')


def count_new(last_visited):
	counts = {}
	for model, items in last_objects().iteritems():
		dates = [i[1] for i in items]
		if model in last_visited:
			counts[model] = len(dates) - bisect_left(dates, parse_datetime(last_visited[model]))
		else:
			counts[model] = None
	return counts


def update_last_visited(user, content_type):
	now = timezone.now()
	user_settings = user.user_settings
	user_settings.setdefault('last_visited', {})
	last_visited = user_settings['last_visited']
	if content_type:
		last_visited[content_type] = now
	for model_name in MODELS:
		last_visited.setdefault(model_name, now)
	user.user_settings = user_settings
	user.save()


def update_visited_items(user, content_type, object_id):
	user_settings = user.user_settings
	user_settings.setdefault('visited_items', [])
	visited_items = set(user_settings['visited_items'])
	visited_items.add(object_id)
	visited_items = visited_items.intersection(set(i[0] for i in last_objects()[content_type]))
	user_settings['visited_items'] = list(visited_items)
	user.user_settings = user_settings
	user.save()


def get_count_new(user):
	last_visited = user.user_settings.get('last_visited', {})
	return count_new(last_visited)
