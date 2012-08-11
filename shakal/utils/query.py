# -*- coding: utf-8 -*-

from django.db.models.query import RawQuerySet
from django.db.models import sql

class RawLimitQuerySet(object):

	def __init__(self, raw_query, count_query, model = None, params = [], translations = None, using = None):
		self.raw_query = raw_query
		self.count_query = count_query
		self.model = model
		self.params = params
		self.translations = translations
		self.db = using
		self._last_k = None
		self._cache = None

	def __len__(self):
		if not hasattr(self, '_count_cache'):
			query = sql.RawQuery(sql = self.count_query, using = self.db, params = self.params)
			self._count_cache = list(query)[0][0]
		return self._count_cache

	def __getitem__(self, k):
		if not isinstance(k, (slice, int, long)):
			raise ValueError
		self._initialize_cache(k)
		self._last_k = k
		return self._cache[k]

	def _initialize_cache(self, k):
		if self._last_k is None or (isinstance(self._last_k, slice) and self._last_k != k):
			self._load_cache(k)

	def _load_cache(self, k):
		query = self.raw_query
		params = self.params[:]
		if isinstance(k, slice):
			if k.stop is not None:
				query += ' LIMIT %s'
				if k.start is None:
					params.append(k.stop)
				else:
					params.append(k.stop - k.start)
			if k.start is not None:
				query += ' OFFSET %s'
				params.append(k.start)
		queryset = RawQuerySet(query, model = self.model, params = params, translations = self.translations, using = self.db)
		self._cache = list(queryset)
