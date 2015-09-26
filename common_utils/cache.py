# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import hashlib
import pickle
from django.core.cache import caches


class LRUCache(collections.MutableMapping):
	def __init__(self, maxsize):
		self.__maxsize = maxsize
		self.__cache = collections.OrderedDict()

	def __getitem__(self, key):
		value = self.__cache.pop(key)
		self.__cache[key] = value
		return value

	def __setitem__(self, key, value):
		self.__cache.pop(key, None)
		self.__cache[key] = value
		if len(self.__cache) > self.__maxsize:
			self.__cache.popitem(last=False)

	def __delitem__(self, key):
		self.__cache.pop(key)

	def __contains__(self, key):
		return key in self.__cache

	def __iter__(self):
		return iter(self.__cache)

	def __len__(self):
		return len(self.__cache)

	def __repr__(self):
		return repr(self.__cache)

	def get(self, key, default=None):
		return self.__cache.get(key, default)


class Cache(object):
	def set(self, name, value, tag=None):
		raise NotImplementedError()

	def get(self, name):
		raise NotImplementedError()

	def delete(self, name):
		raise NotImplementedError()

	def delete_tag(self, tag):
		raise NotImplementedError()

	def sync(self):
		pass #noop


class SimpleCache(Cache):
	def __init__(self):
		self.__data = {}
		self.__data['__tags__'] = {}

	def set(self, name, value, tag=None):
		self.__data[name] = value
		if tag is not None:
			self.__data['__tags__'].setdefault(tag, [])
			self.__data['__tags__'][tag].append(name)

	def get(self, name):
		return self.__data[name]

	def delete(self, name):
		del self.__data[name]
		for lst in self.__data['__tags__'].values():
			if name in lst:
				lst.remove(name)

	def delete_tag(self, tag):
		tags = self.__data['__tags__']
		if not tag in tags:
			return
		for name in tags[tag]:
			del self.__data[name]
		self.__data['__tags__'][tag] = []


class DjangoCache(Cache):
	CACHE_MAX_AGE = 3600

	def __init__(self):
		self.cache = caches['default']
		self.tags = {}

	def set(self, name, value, tag=None):
		self.cache.set(name, value, self.CACHE_MAX_AGE)
		if tag is not None:
			self.tags.setdefault(tag, [])
			self.tags[tag].append(name)

	def get(self, name):
		val = self.cache.get(name)
		if val is None:
			raise KeyError
		return val

	def delete(self, name):
		self.cache.delete(name)
		for lst in self.tags.values():
			if name in lst:
				lst.remove(name)

	def delete_tag(self, tag):
		tags = self.tags
		if not tag in tags:
			return
		for name in tags[tag]:
			self.cache.delete(name)
		self.tags[tag] = []


def cached_fn_raw(fun, cache, tag=None, name=None, is_method=False):
	def wrap(*args, **kwargs):
		cache_name = name or fun.__module__ + '.' + fun.__name__
		fn_args = args
		if is_method:
			fn_args = args[1:]
		if fn_args or kwargs:
			cache_name += hashlib.sha1(pickle.dumps(fn_args) + pickle.dumps(kwargs)).hexdigest()
		try:
			return cache.get(cache_name)
		except KeyError:
			ret = fun(*args, **kwargs)
			cache.set(cache_name, ret, tag=tag)
			return ret
	return wrap


def cached_fn_factory(cache):
	def decorator(tag=None, name=None):
		def cached_fn_wrap(fun):
			return cached_fn_raw(fun, cache, tag=tag, name=name)
		return cached_fn_wrap
	return decorator


def cached_method_factory(cache):
	def decorator(tag=None, name=None):
		def cached_fn_wrap(fun):
			return cached_fn_raw(fun, cache, tag=tag, name=name, is_method=True)
		return cached_fn_wrap
	return decorator


def delete_tag_handler_factory(cache):
	def delete_tag_handler(name):
		def delete_tag_wrap(*args, **kwargs):
			cache.delete_tag(name)
		return delete_tag_wrap
	return delete_tag_handler


cache_instance = SimpleCache()
cached_fn = cached_fn_factory(cache_instance)
cached_method = cached_method_factory(cache_instance)
delete_tag_factory = delete_tag_handler_factory(cache_instance)
