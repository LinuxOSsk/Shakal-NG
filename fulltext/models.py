# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex
from django.db import models

from .managers import SearchIndexManager


try:
	from django.contrib.postgres.search import SearchVectorField
except ImportError:
	SearchVectorField = models.TextField


class AbstractSearchIndex(models.Model):
	HIGHLIGHT_START = '\x1bs'
	HIGHLIGHT_STOP = '\x1be'

	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')
	language_code = models.CharField(max_length=10)

	def get_updated_field(self):
		raise NotImplementedError()

	class Meta:
		abstract = True
		unique_together = (('content_type', 'object_id'),)


class SearchIndex(AbstractSearchIndex):
	objects = SearchIndexManager()

	# metadata
	created = models.DateTimeField(blank=True, null=True)
	updated = models.DateTimeField(blank=True, null=True)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
	authors_name = models.CharField(max_length=255)

	# document
	title = models.TextField()
	document = models.TextField()
	comments = models.TextField()
	document_search_vector = SearchVectorField()
	comments_search_vector = SearchVectorField()
	combined_search_vector = SearchVectorField()

	@staticmethod
	def get_updated_field():
		return 'updated'

	class Meta:
		indexes = [
			GinIndex(fields=['document_search_vector']),
			GinIndex(fields=['comments_search_vector']),
			GinIndex(fields=['combined_search_vector']),
		]
