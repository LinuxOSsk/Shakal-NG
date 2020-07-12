# -*- coding: utf-8 -*-
from django.contrib.postgres.search import SearchVector
from django.db import models


class SearchIndexQuerySet(models.QuerySet):
	def update_search_index(self):
		self.update(
			document_search_vector=SearchVector('title', weight='A') + SearchVector('document', weight='D'),
			comments_search_vector=SearchVector('comments', weight='A'),
			combined_search_vector=SearchVector('title', weight='A') + SearchVector('document', weight='C') + SearchVector('comments', weight='D'),
		)


class SearchIndexManager(models.Manager.from_queryset(SearchIndexQuerySet)):
	def update_search_index(self):
		return self.all().update_search_index()
