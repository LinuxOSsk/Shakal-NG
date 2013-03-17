# -*- coding: utf-8 -*-
from datetime import datetime

from haystack import indexes

from article.models import Article


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
	created = indexes.DateTimeField(model_attr = 'pub_time')
	updated = indexes.DateTimeField(model_attr = 'updated')
	author = indexes.CharField(model_attr = 'authors_name')
	title = indexes.CharField(model_attr = 'title')
	text = indexes.CharField(document = True, use_template = True)

	def get_model(self):
		return Article

	def index_queryset(self):
		return self.get_model().objects.filter(pub_time__lte = datetime.now(), published = True)
