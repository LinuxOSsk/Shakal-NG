# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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


def count_new(last_visited, visited_items):
	counts = {}
	for model, items in last_objects().iteritems():
		count = None
		count = 0
		if model in last_visited:
			visited_date = parse_datetime(last_visited[model])
		else:
			visited_date = None
		visited_ids = set(visited_items.get(model, []))
		for pk, date in items:
			if (visited_date is None or date > visited_date) and not pk in visited_ids:
				count += 1
		counts[model] = count
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
	user_settings.setdefault('visited_items', {})
	visited_items = user_settings['visited_items']
	content_visited_items = set(visited_items.get(content_type, []))
	content_visited_items.add(object_id)
	content_visited_items = content_visited_items.intersection(set(i[0] for i in last_objects()[content_type]))
	user_settings['visited_items'][content_type] = list(content_visited_items)
	user.user_settings = user_settings
	user.save()


def get_count_new(user):
	user_settings = user.user_settings
	last_visited = user_settings.get('last_visited', {})
	visited_items = user_settings.get('visited_items', {})
	return count_new(last_visited, visited_items)
