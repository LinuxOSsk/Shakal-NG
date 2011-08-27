# -*- coding: utf-8 -*-
import mptt
import datetime

from django.db import models
from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.comments.managers import CommentManager

class HideRootQuerySet(models.query.QuerySet):
	""" QuerySet s iteraátorom preskakujúcim koreňovú položku """
	def __init__(self, model = None, query = None, using = None):
		super(HideRootQuerySet, self).__init__(model = model, query = query, using = using)
		self.root_item = None
		self.__cache = None

	def has_root_item(self):
		if self.root_item is None:
			if self.__cache is None:
				if super(HideRootQuerySet, self).__len__() > 0:
					return True
				else:
					return False
			else:
				return False
		return True

	def get_root_item(self):
		if self.root_item is not None:
			return self.root_item
		if self.__cache is None:
			self.__cache = []
			for item in super(HideRootQuerySet, self).iterator():
				if item.parent is None:
					self.root_item = item
				self.__cache.append(item)
		return self.root_item

	def set_root_item(self, root_item):
		self.root_item = root_item

	def iterator(self):
		if self.__cache is not None:
			for item in self.__cache:
				if item.parent is not None:
					yield item
				else:
					self.root_item = item
			return
		for item in super(HideRootQuerySet, self).iterator():
			if item.parent_id is not None:
				yield item
			else:
				self.root_item = item

class ThreadedCommentManager(CommentManager):
	use_for_related_fields = True

	def __init__(self, qs_class = models.query.QuerySet):
		self.__qs_class = qs_class
		super(ThreadedCommentManager, self).__init__()

	def get_root_comment(self, ctype, object_pk):
		root_comment, created = self.model.objects.get_or_create(
			parent = None,
			content_type = ctype,
			object_pk = object_pk,
			defaults = {
				'comment': '-',
				'user_name': '-',
				'user_email': 'no@user.no',
				'user_url': '',
				'submit_date': datetime.datetime.now(),
				'site_id': settings.SITE_ID
			}
		)
		return root_comment

	def get_query_set(self):
		return self.__qs_class(self.model)

class ThreadedComment(Comment):
	title = models.CharField(max_length = 100)
	parent = models.ForeignKey('self', related_name = 'children', blank = True, null = True)
	objects = ThreadedCommentManager()
	comment_objects = ThreadedCommentManager(HideRootQuerySet)
	def is_root(self):
		return self.parent is None

	class Meta:
		ordering = ('tree_id', 'lft')

mptt.register(ThreadedComment)

