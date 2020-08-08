# -*- coding: utf-8 -*-
from django.contrib.postgres.search import SearchVector
from django.db import models, connections


class SearchIndexQuerySet(models.QuerySet):
	def update_search_index(self):
		connection = connections[self.db]
		if connection.vendor == 'postgresql':
			configs = self.order_by('language_code').values_list('language_code', flat=True).distinct()
			for config in configs:
				SV = type('SV', (SearchVector,), {'config': config})
				self.update(
					document_search_vector=SV('title', weight='A') + SV('document', weight='D'),
					comments_search_vector=SV('comments', weight='A'),
					combined_search_vector=SV('title', weight='A') + SV('document', weight='C') + SV('comments', weight='D'),
				)


class SearchIndexManager(models.Manager.from_queryset(SearchIndexQuerySet)):
	def update_search_index(self):
		return self.all().update_search_index()
