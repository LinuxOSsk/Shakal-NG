# -*- coding: utf-8 -*-
from django.contrib.postgres.search import SearchVector
from django.db import models, connections


class SV(SearchVector):
	config = models.F('language_code')


class SearchIndexQuerySet(models.QuerySet):
	def update_search_index(self):
		connection = connections[self.db]
		if connection.vendor == 'postgresql':
			self.update(
				document_search_vector=SV('title', weight='A') + SV('document', weight='D'),
				comments_search_vector=SV('comments', weight='A'),
				combined_search_vector=SV('title', weight='A') + SV('document', weight='C') + SV('comments', weight='D'),
			)


class SearchIndexManager(models.Manager.from_queryset(SearchIndexQuerySet)):
	def update_search_index(self):
		return self.all().update_search_index()
