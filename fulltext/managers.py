# -*- coding: utf-8 -*-
from django.db import models, connections

from .functions import Unaccent


class SearchIndexQuerySet(models.QuerySet):
	def update_search_index(self):
		connection = connections[self.db]
		if connection.vendor == 'postgresql':
			from django.contrib.postgres.search import SearchVector

			SV = SearchVector
			configs = self.order_by('language_code').values_list('language_code', flat=True).distinct()
			for config in configs:
				self.update(
					document_search_vector=SV(Unaccent('title'), weight='A', config=config) + SV(Unaccent('document'), weight='D', config=config),
					comments_search_vector=SV(Unaccent('comments'), weight='A', config=config),
					combined_search_vector=SV(Unaccent('title'), weight='A', config=config) + SV(Unaccent('document'), weight='C', config=config) + SV(Unaccent('comments'), weight='D', config=config),
				)


class SearchIndexManager(models.Manager.from_queryset(SearchIndexQuerySet)):
	def update_search_index(self):
		return self.all().update_search_index()
