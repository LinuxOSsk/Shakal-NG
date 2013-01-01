# -*- coding: utf-8 -*-

from shakal.news.models import News
from haystack import indexes


class NewsIndex(indexes.SearchIndex, indexes.Indexable):
	created = indexes.DateTimeField(model_attr = 'created')
	updated = indexes.DateTimeField(model_attr = 'updated')
	author = indexes.CharField(model_attr = 'authors_name')
	title = indexes.CharField(model_attr = 'title')
	text = indexes.CharField(document = True, use_template = True)

	def get_model(self):
		return News

	def index_queryset(self):
		return self.get_model().objects.filter(approved = True)
