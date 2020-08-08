# -*- coding: utf-8 -*-

from blog.models import Blog, Post
from fulltext import indexes, register as fulltext_register


class BlogIndex(indexes.SearchIndex):
	model = Blog

	created = indexes.ModelField(model_field='created')
	updated = indexes.ModelField(model_field='updated')
	author = indexes.ModelField(model_field='author')
	authors_name = indexes.TemplateField()
	title = indexes.ModelField(model_field='title')
	document = indexes.TemplateField(model_field='filtered_description')

	def get_index_queryset(self, using=None):
		return (self.get_model().objects
			.prefetch_related(indexes.AuthorPrefetch())
			.using(using))


class PostIndex(indexes.SearchIndex):
	model = Post

	created = indexes.ModelField(model_field='created')
	updated = indexes.ModelField(model_field='updated')
	author = indexes.ModelField(model_field='blog__author')
	authors_name = indexes.TemplateField()
	title = indexes.ModelField(model_field='title')
	document = indexes.TemplateField(model_field='filtered_content')
	comments = indexes.CommentsField()

	def get_index_queryset(self, using=None):
		return (self.get_model().objects
			.prefetch_related(indexes.CommentsPrefetch(), 'blog', indexes.AuthorPrefetch('blog__author'))
			.using(using)
			.published())


fulltext_register(BlogIndex)
fulltext_register(PostIndex)
