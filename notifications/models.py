# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db import models
from django.utils.translation import ugettext_lazy as _


class EventManager(models.Manager):
	def __get_active_users(self):
		return get_user_model().objects.filter(is_active = True)

	def __generate_inbox_objects(self, users, event_id):
		user_ids = users.values_list('pk', flat = True)
		for user_id in user_ids:
			yield Inbox(event_id = event_id, recipient_id = user_id)

	def broadcast(self, message, object_id = None, content_type = None, action = None, level = messages.INFO, author = None):
		event = Event(author = author)
		event.object_id = object_id
		event.content_type = content_type
		if action:
			event.action = action
		if level:
			event.level = level
		event.message = message
		event.save()

		users = self.__get_active_users()
		if author:
			users = users.exclude(pk = author.pk)
		Inbox.objects.bulk_create(self.__generate_inbox_objects(users, event.pk))


class Event(models.Model):
	OTHER_ACTION = 'x'
	CREATE_ACTION = 'c'
	UPDATE_ACTION = 'u'
	DELETE_ACTION = 'd'
	MESSAGE_ACTION = 'm'
	ADD_COMMENT_ACTION = 'a'

	ACTION_TYPE = (
		(OTHER_ACTION, _('other')),
		(CREATE_ACTION, _('create')),
		(UPDATE_ACTION, _('update')),
		(DELETE_ACTION, _('delete')),
		(MESSAGE_ACTION, _('message')),
		(ADD_COMMENT_ACTION, _('comment')),
	)

	objects = EventManager()

	object_id = models.PositiveIntegerField(blank = True, null = True)
	content_type = models.ForeignKey(ContentType, blank = True, null = True)
	time = models.DateTimeField(auto_now_add = True)
	content_object = generic.GenericForeignKey('content_type', 'object_id')
	action = models.CharField(max_length = 1, choices = ACTION_TYPE, default = MESSAGE_ACTION)
	level = models.IntegerField(default = messages.INFO)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True)
	message = models.TextField()

	class Meta:
		index_together = [['object_id', 'content_type', 'action', 'level']]


class InboxManager(models.Manager):
	def user_messages(self, user):
		return self.get_query_set() \
			.select_related('event', 'event__content_type') \
			.filter(recipient = user) \
			.order_by('readed', '-pk')


class Inbox(models.Model):
	objects = InboxManager()

	recipient = models.ForeignKey(settings.AUTH_USER_MODEL)
	event = models.ForeignKey(Event)
	readed = models.BooleanField(default = False)

	def content_type(self):
		if not self.event.content_type:
			return None
		return self.event.content_type.app_label + '.' + self.event.content_type.model

	@models.permalink
	def get_absolute_url(self):
		return ('notifications:read', None, {'pk': self.pk})
