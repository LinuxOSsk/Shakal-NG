# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class EventManager(models.Manager):
	def __get_active_users(self):
		return get_user_model().objects.filter(is_active=True)

	def __generate_inbox_objects(self, users, event_id):
		user_ids = users.values_list('pk', flat=True)
		for user_id in user_ids:
			yield Inbox(event_id=event_id, recipient_id=user_id)

	def create_event(self, message, content_object, **kwargs):
		event = Event(message=message, **kwargs)
		if content_object is not None:
			event.object_id = content_object.pk
			event.content_type = ContentType.objects.get_for_model(content_object)
		return event

	def filter_users(self, is_staff, is_superuser, permissions):
		users = self.__get_active_users()
		if is_staff is not None:
			users = users.filter(is_staff=is_staff)
		if is_superuser is not None:
			users = users.filter(is_superuser=is_superuser)
		if permissions is not None:
			ct = ContentType.objects.get_for_model(permissions[0])
			perm = Permission.objects.get(content_type=ct, codename=permissions[1])
			users = users.filter(Q(user_permissions=perm) | Q(groups__permissions=perm) | Q(is_superuser=True)).distinct()
		return users

	def exclude_duplicate_events(self, users, event):
		if event.content_object:
			excluded = get_user_model().objects.filter(
				Q(
					inbox__event__object_id=event.object_id,
					inbox__event__content_type_id=event.content_type_id,
					inbox__event__action=event.action,
					inbox__readed=False
				) |
				Q(inbox__event=event)
			)
			users = users.exclude(pk__in=excluded)
		return users

	def notify_users(self, users, event):
		Inbox.objects.bulk_create(self.__generate_inbox_objects(users, event.pk))

	def broadcast(self, message, content_object=None, action=None, level=messages.INFO, author=None, users=None, is_staff=None, is_superuser=None, permissions=None): #pylint: disable=too-many-arguments
		event = self.create_event(message, content_object, action=action, level=level, author=author)
		event.save()
		self.broadcast_event(event, users, is_staff, is_superuser, permissions)

	def broadcast_event(self, event, users=None, is_staff=None, is_superuser=None, permissions=None):
		if users is None:
			users = self.filter_users(is_staff, is_superuser, permissions)
		users = self.exclude_duplicate_events(users, event)
		if event.author_id:
			users = users.exclude(pk=event.author_id)
		self.notify_users(users, event)

	def deactivate(self, content_object, action_type=None):
		if isinstance(content_object, models.Model):
			events = Event.objects.filter(object_id=content_object.pk, content_type=ContentType.objects.get_for_model(content_object))
		elif isinstance(content_object, tuple):
			events = Event.objects.filter(object_id=content_object[0], content_type=content_object[1])
		else:
			raise TypeError("Wrong type of content object")
		if action_type is not None:
			events = events.filter(action=action_type)
		events.update(level=0)
		Inbox.objects.filter(event__in=events).update(readed=True)


class Event(models.Model):
	OTHER_ACTION = 'x'
	CREATE_ACTION = 'c'
	UPDATE_ACTION = 'u'
	DELETE_ACTION = 'd'
	MESSAGE_ACTION = 'm'
	ADD_COMMENT_ACTION = 'a'
	FLAG_ACTION = 'f'

	ACTION_TYPE = (
		(OTHER_ACTION, _("other")),
		(CREATE_ACTION, _("create")),
		(UPDATE_ACTION, _("update")),
		(DELETE_ACTION, _("delete")),
		(MESSAGE_ACTION, _("message")),
		(ADD_COMMENT_ACTION, _("comment")),
		(FLAG_ACTION, _("flag")),
	)

	objects = EventManager()

	object_id = models.PositiveIntegerField(
		verbose_name="ID objektu",
		blank=True,
		null=True
	)
	content_type = models.ForeignKey(
		ContentType,
		verbose_name="typ obsahu",
		blank=True,
		null=True,
		on_delete=models.PROTECT
	)
	content_object = GenericForeignKey('content_type', 'object_id')

	linked_id = models.PositiveIntegerField(
		verbose_name="ID odkazovaného objektu",
		blank=True,
		null=True
	)
	linked_type = models.ForeignKey(
		ContentType,
		verbose_name="typ odkazovaného obsahu",
		related_name='+',
		blank=True,
		null=True,
		on_delete=models.PROTECT
	)
	linked_object = GenericForeignKey('linked_type', 'linked_id')

	time = models.DateTimeField(
		auto_now_add=True
	)
	action = models.CharField(
		verbose_name="akcia",
		max_length=1,
		choices=ACTION_TYPE,
		default=MESSAGE_ACTION
	)
	level = models.IntegerField(
		verbose_name="úroveň",
		default=messages.INFO
	)
	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name="autor",
		blank=True,
		null=True,
		on_delete=models.SET_NULL
	)
	message = models.TextField(
		verbose_name="správa",
	)

	class Meta:
		index_together = (('object_id', 'content_type', 'action', 'level'),)
		verbose_name = "udalosť"
		verbose_name_plural = "udalosti"

	def __str__(self):
		return self.message


class InboxManager(models.Manager):
	def user_messages(self, user):
		return (self.get_queryset()
			.select_related('event', 'event__content_type')
			.filter(recipient=user)
			.order_by('readed', '-pk'))


class Inbox(models.Model):
	objects = InboxManager()

	recipient = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name="príjemca",
		related_name='inbox',
		on_delete=models.CASCADE
	)
	event = models.ForeignKey(
		Event,
		verbose_name="udalosť",
		on_delete=models.CASCADE
	)
	readed = models.BooleanField(
		verbose_name="prečítané",
		default=False
	)

	def __str__(self):
		return str(self.event_id)

	@property
	def content_type(self):
		if not self.event.content_type:
			return None
		return self.event.content_type.app_label + '.' + self.event.content_type.model

	def get_absolute_url(self):
		return reverse('notifications:read', kwargs={'pk': self.pk})

	class Meta:
		verbose_name = "schránka"
		verbose_name_plural = "schránky"
