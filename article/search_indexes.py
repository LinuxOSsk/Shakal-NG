# -*- coding: utf-8 -*-
from django.utils import timezone
from haystack import indexes

from .models import Article


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
	created = indexes.DateTimeField(model_attr='pub_time')
	updated = indexes.DateTimeField(model_attr='updated')
	author = indexes.CharField(model_attr='authors_name')
	title = indexes.CharField(model_attr='title')
	text = indexes.CharField(document=True, use_template=True)

	def get_updated_field(self):
		return 'updated'

	def get_model(self):
		return Article

	def index_queryset(self, using=None):
		return (self.get_model().objects.all()
			.filter(pub_time__lte=timezone.now(), published=True))
