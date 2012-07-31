# -*- coding: utf-8 -*-

import datetime
import mptt

from django.db import models
from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.comments.managers import CommentManager


class HideRootQuerySet(models.query.QuerySet):
	def __init__(self, *args, **kwargs):
		super(HideRootQuerySet, self).__init__(*args, **kwargs)
		self.__root_item = None
		self.__cache = None

	def has_root_item(self):
		return self.get_root_item() is not None

	def get_root_item(self):
		self.__load_cache_and_root_item()
		return self.__root_item

	def iterator(self):
		self.__load_cache_and_root_item()
		for item in self.__cache:
			if not self.__is_root(item):
				yield item

	def __load_cache_and_root_item(self):
		if self.__cache is not None:
			return
		self.__cache = []
		for item in super(HideRootQuerySet, self).iterator():
			if self.__is_root(item):
				self.__root_item = item
			self.__cache.append(item)

	def __is_root(self, item):
		return item.parent is None


class ThreadedCommentManager(CommentManager):
	use_for_related_fields = True

	def __init__(self, qs_class = models.query.QuerySet):
		self.__qs_class = qs_class
		super(ThreadedCommentManager, self).__init__()

	def get_root_comment(self, ctype, object_pk):
		root_comment, created = self.model.objects.get_or_create(
			parent = None,
			is_locked = False,
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
	subject = models.CharField(max_length = 100)
	parent = models.ForeignKey('self', related_name = 'children', blank = True, null = True)
	is_locked = models.BooleanField(default = False)
	objects = ThreadedCommentManager()
	comment_objects = ThreadedCommentManager(HideRootQuerySet)

	class Meta:
		ordering = ('tree_id', 'lft')

mptt.register(ThreadedComment)
