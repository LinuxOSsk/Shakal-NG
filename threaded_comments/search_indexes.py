# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from haystack import indexes

from threaded_comments.models import RootHeader


class CommentIndex(indexes.SearchIndex, indexes.Indexable):
	created = indexes.DateTimeField()
	updated = indexes.DateTimeField(model_attr='last_comment')
	author = indexes.CharField()
	title = indexes.CharField()
	text = indexes.CharField(document=True, use_template=True)

	def get_updated_field(self):
		return 'last_comment'

	def get_model(self):
		return RootHeader

	def index_queryset(self, using=None):
		return self.get_model().objects.all()

	def prepare_created(self, object):
		content_object = object.content_object
		if hasattr(content_object, 'created'):
			return content_object.created
		else:
			return None

	def prepare_author(self, object):
		content_object = object.content_object
		if hasattr(content_object, 'authors_name'):
			return content_object.authors_name
		else:
			return None

	def prepare_title(self, object):
		content_object = object.content_object
		if hasattr(content_object, 'title'):
			return content_object.title
		else:
			return None
