# -*- coding: utf-8 -*-
# pylint: disable=abstract-method,too-many-locals,protected-access,no-member,unused-argument
from __future__ import unicode_literals

from django.db.models import Q
from django.utils import six
from haystack import connections
from haystack.backends import BaseEngine
from haystack.backends.simple_backend import SimpleSearchBackend as CoreSimpleSearchBackend, SimpleSearchQuery
from haystack.models import SearchResult
from haystack.utils import get_model_ct_tuple


class SimpleSearchBackend(CoreSimpleSearchBackend):
	def search(self, query_string, **kwargs):
		hits = 0
		results = []
		result_class = SearchResult
		models = connections[self.connection_alias].get_unified_index().get_indexed_models()

		if kwargs.get('result_class'):
			result_class = kwargs['result_class']

		if kwargs.get('models'):
			models = kwargs['models']

		if query_string:
			for model in models:
				if query_string == '*':
					qs = model.objects.all()
				else:
					for term in query_string.split():
						queries = []

						for field in model._meta.fields:
							if hasattr(field, 'related'):
								continue

							if not field.get_internal_type() in ('TextField', 'CharField', 'SlugField'):
								continue

							queries.append(Q(**{'%s__icontains' % field.name: term}))

						qs = model.objects.filter(six.moves.reduce(lambda x, y: x | y, queries)) if queries else qs.none()

				hits += len(qs)

				for match in qs:
					match.__dict__.pop('score', None)
					app_label, model_name = get_model_ct_tuple(match)
					result = result_class(app_label, model_name, match.pk, 0, **match.__dict__)
					# For efficiency.
					result._model = match.__class__
					result._object = match
					results.append(result)

		return {
			'results': results,
			'hits': hits,
		}

	def update(self, index, iterable, commit=True):
		pass

	def clear(self, models=None, commit=True):
		pass


class SimpleEngine(BaseEngine):
	backend = SimpleSearchBackend
	query = SimpleSearchQuery
