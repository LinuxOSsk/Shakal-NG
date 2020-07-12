# -*- coding: utf-8 -*-
from django.utils import timezone

from .models import Article
from fulltext import indexes, register as fulltext_register


class ArticleIndex(indexes.SearchIndex):
	model = Article

	created = indexes.ModelField(model_field='pub_time')
	updated = indexes.ModelField(model_field='updated')
	author = indexes.ModelField(model_field='author')
	authors_name = indexes.ModelField(model_field='authors_name')
	title = indexes.ModelField(model_field='title')
	document = indexes.TemplateField(model_field='filtered_content')

	def get_index_queryset(self, using=None):
		return (self.get_model().objects.using(using)
			.filter(pub_time__lte=timezone.now(), published=True))


fulltext_register(ArticleIndex)
