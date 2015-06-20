# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from cachetools import LRUCache
from django.core.cache import caches


default_cache = caches['default']


def get_cache():
	cache = default_cache.get('hitcount_cache')
	if not cache:
		cache = LRUCache(maxsize=1000)
	return cache


def set_cache(cache):
	default_cache.set('hitcount_cache', cache)
