# -*- coding: utf-8 -*-
from .models import Topic
from fulltext import indexes, register as fulltext_register


class TopicIndex(indexes.SearchIndex):
	model = Topic

	created = indexes.ModelField(model_field='created')
	updated = indexes.ModelField(model_field='updated')
	author = indexes.ModelField(model_field='author')
	authors_name = indexes.ModelField(model_field='authors_name')
	title = indexes.ModelField(model_field='title')
	document = indexes.TemplateField(model_field='filtered_text')
	comments = indexes.CommentsField()

	def get_index_queryset(self, using=None):
		return (self.get_model().objects.using(using)
			.prefetch_related(indexes.CommentsPrefetch(), indexes.AuthorPrefetch()))


fulltext_register(TopicIndex)
