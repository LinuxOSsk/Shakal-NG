# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.cache import caches

from common_utils.cache import LRUCache


default_cache = caches['default']


def get_cache():
	cache = default_cache.get('hitcount_cache')
	if not cache:
		cache = LRUCache(maxsize=1000)
	return cache


def set_cache(cache):
	default_cache.set('hitcount_cache', cache)


def set_hitcount(object_id, content_type_id, count):
	cache = get_cache()
	cache[object_id, content_type_id] = count
	set_cache(cache)
