# -*- coding: utf-8 -*-
from .models import Node
from fulltext import indexes, register as fulltext_register


class NodeIndex(indexes.SearchIndex):
	model = Node

	created = indexes.ModelField(model_field='created')
	updated = indexes.ModelField(model_field='updated')
	title = indexes.ModelField(model_field='title')
	document = indexes.TemplateField(model_field='text')

	def get_index_queryset(self, using=None):
		return self.get_model().objects.using(using).filter(node_type='story').select_related('revision')


fulltext_register(NodeIndex)
