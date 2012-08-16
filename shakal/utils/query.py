# -*- coding: utf-8 -*-

from django.db.models import sql

class RawLimitQuerySet(object):

	def __init__(self, raw_query, count_query, model_definition = None, params = [], translations = None, using = None):
		self.raw_query = raw_query
		self.count_query = count_query
		self.model_definition = model_definition
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

	def count(self):
		return len(self)

	def get_raw_query(self):
		return self.raw_query

	def get_model_definition(self):
		return self.model_definition

	def __getitem__(self, k):
		if not isinstance(k, (slice, int, long)):
			raise ValueError
		self._initialize_cache(k)
		if isinstance(self._last_k, slice):
			return self._cache
		else:
			return self._cache[k]

	def _initialize_cache(self, k):
		if self._last_k is None or (isinstance(self._last_k, slice) and self._last_k != k):
			self._load_cache(k)
			self._last_k = k

	def _load_cache(self, k):
		query = self.get_raw_query()
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
		queryset = sql.RawQuery(sql = query, using = self.db, params = params)
		self._cache = []
		for item in queryset:
			column = 0
			model_args = {}
			model_definition = self.get_model_definition()
			model = model_definition[0]
			fields = model_definition[1:]
			for field in fields:
				if field is None:
					continue
				if isinstance(field, list):
					submodel_args = {}
					submodel = field[0]
					submodel_field = field[1]
					subfields = field[2:]
					for subfield in subfields:
						submodel_args[subfield] = item[column]
						column += 1
					model_args[submodel_field] = submodel(**submodel_args)
					continue
				else:
					model_args[field] = item[column]
				column += 1
			extra_fields = {}
			model_fields = {}
			model_field_names = set(model._meta.get_all_field_names())
			for name, value in model_args.iteritems():
				if name in model_field_names:
					model_fields[name] = value
				else:
					extra_fields[name] = value
			instance = model(**model_fields)
			for name, value in extra_fields.iteritems():
				setattr(instance, name, value)
			self._cache.append(instance)
