# -*- coding: utf-8 -*-
from haystack import indexes

from .models import Desktop


class DesktopIndex(indexes.SearchIndex, indexes.Indexable):
	created = indexes.DateTimeField(model_attr='created')
	updated = indexes.DateTimeField(model_attr='updated')
	title = indexes.CharField(model_attr='title')
	text = indexes.CharField(document=True, use_template=True)

	def get_updated_field(self):
		return 'updated'

	def get_model(self):
		return Desktop

	def index_queryset(self, using=None):
		return self.get_model().objects.all()
