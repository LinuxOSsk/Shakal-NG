# -*- coding: utf-8 -*-

import mptt
from attachment.models import Attachment
from datetime import datetime
from django.db import models
from django.db.models import Count, Max
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.comments.managers import CommentManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


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
		return item.parent_id is None


class CommentManager(CommentManager):
	def get_query_set(self):
		return (super(CommentManager, self).get_query_set().select_related('user__profile__pk'))
Comment.add_to_class('objects', CommentManager())


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
				'submit_date': datetime.now(),
				'site_id': settings.SITE_ID
			}
		)
		return root_comment

	def get_query_set(self):
		queryset = self.__qs_class(self.model).select_related('user__profile')
		return queryset


class ThreadedComment(Comment):
	subject = models.CharField(max_length = 100)
	parent = models.ForeignKey('self', related_name = 'children', blank = True, null = True)
	is_locked = models.BooleanField(default = False)
	objects = ThreadedCommentManager()
	comment_objects = ThreadedCommentManager(HideRootQuerySet)
	plain_objects = models.Manager()
	attachments = generic.GenericRelation(Attachment)
	updated = models.DateTimeField(editable = False)

	def get_absolute_url(self):
		return reverse('comment', args = [self.pk], kwargs = {}) + "#link_" + str(self.id)

	def save(self, *args, **kwargs):
		self.updated = datetime.now()
		if not self.id:
			self.submit_date = self.updated
		return super(ThreadedComment, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.subject

	class Meta:
		ordering = ('tree_id', 'lft')
mptt.register(ThreadedComment)


class RootHeader(models.Model):
	last_comment = models.DateTimeField(null = True, blank = True, db_index = True)
	comment_count = models.PositiveIntegerField(default = 0, db_index = True)
	is_locked = models.BooleanField(default = False)
	is_resolved = models.BooleanField(default = False)
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey('content_type', 'object_id')

	@models.permalink
	def get_absolute_url(self):
		return ('comments', [self.pk], {})

	class Meta:
		unique_together = (('content_type', 'object_id'),)
		verbose_name = _('comment')
		verbose_name_plural = _('comments')


def update_comments_header(sender, **kwargs):
	instance = kwargs['instance']
	if instance.parent is None:
		root = instance
	else:
		root = ThreadedComment.objects.get(content_type = instance.content_type, object_pk = instance.object_pk, parent = None)
	statistics = ThreadedComment.objects
	statistics = statistics.filter(content_type = root.content_type, object_pk = root.object_pk, is_public = True, is_removed = False)
	statistics = statistics.exclude(pk = root.pk)
	statistics = statistics.aggregate(Count('pk'), Max('submit_date'))

	header, created = RootHeader.objects.get_or_create(content_type = root.content_type, object_id = root.object_pk)
	header.is_locked = root.is_locked
	header.last_comment = statistics['submit_date__max']
	if header.last_comment is None:
		content_object = root.content_object
		if hasattr(content_object, 'time'):
			header.last_comment = content_object.time
	header.comment_count = statistics['pk__count']
	header.save()

post_save.connect(update_comments_header, sender = ThreadedComment)


class UserDiscussionAttribute(models.Model):
	user = models.ForeignKey(User)
	discussion = models.ForeignKey(RootHeader)
	time = models.DateTimeField(null = True, blank = True)
	watch = models.BooleanField(default = False)

	class Meta:
		unique_together = (('user', 'discussion'),)
