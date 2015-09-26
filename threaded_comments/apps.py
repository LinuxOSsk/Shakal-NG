# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete


from notifications.models import Event


class CommentsConfig(AppConfig):
	name = 'threaded_comments'
	verbose_name = 'Komentáre'

	def ready(self):
		from .utils import update_comments_header
		Comment = self.get_model('Comment')
		post_save.connect(update_comments_header, sender=Comment)
		post_delete.connect(update_comments_header, sender=Comment)
		post_save.connect(self.send_notifications, sender=Comment)

	def send_notifications(self, sender, instance, created, **kwargs): #pylint: disable=unused-argument
		if not created:
			return
		watchers = get_user_model().objects.\
			filter(userdiscussionattribute__discussion=instance.get_or_create_root_header(), userdiscussionattribute__watch=True).\
			distinct()
		title = u"Pridaný komentár v diskusii " + unicode(instance.content_object)
		author = None
		if instance.user:
			author = instance.user
		Event.objects.broadcast(title, instance.content_object, action=Event.CREATE_ACTION, author=author, users=watchers)
