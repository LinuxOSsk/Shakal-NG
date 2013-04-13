# -*- coding: utf-8 -*-


from shakal.forum.models import Topic
from haystack import indexes


class TopicIndex(indexes.SearchIndex, indexes.Indexable):
	created = indexes.DateTimeField(model_attr = 'created')
	updated = indexes.DateTimeField(model_attr = 'updated')
	author = indexes.CharField(model_attr = 'authors_name')
	title = indexes.CharField(model_attr = 'title')
	text = indexes.CharField(document = True, use_template = True)

	def get_model(self):
		return Topic

	def index_queryset(self, using = None):
		return self.get_model().objects.all()
