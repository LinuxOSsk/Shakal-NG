# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.db import transaction
from django.db.models import Count, Max
from django.db.models.signals import post_save, post_delete


#from notifications.models import Event


class CommentsConfig(AppConfig):
	name = 'threaded_comments'
	verbose_name = 'Komentáre'

	def ready(self):
		Comment = self.get_model('Comment')
		post_save.connect(self.update_comments_header, sender=Comment)
		post_delete.connect(self.update_comments_header, sender=Comment)
		#post_save.connect(send_notifications, sender=Comment)

	def update_comments_header(self, sender, instance, **kwargs):
		Comment = sender
		RootHeader = self.get_model('RootHeader')

		if instance.parent is None:
			root = instance
		else:
			root = Comment.objects.get(content_type=instance.content_type, object_id=instance.object_id, parent=None)

		statistics = Comment.objects.\
			filter(content_type=root.content_type, object_id=root.object_id, is_public=True, is_removed=False).\
			exclude(pk=root.pk).\
			aggregate(Count('pk'), Max('submit_date'))

		last_comment = statistics['submit_date__max']
		if last_comment is None:
			content_object = root.content_object
			last_comment = getattr(content_object, 'created', getattr(content_object, 'time', getattr(content_object, 'pub_time', None)))

		with transaction.atomic():
			header, _ = RootHeader.objects.get_or_create(
				content_type=root.content_type,
				object_id=root.object_id,
				defaults={'pub_date': root.submit_date, 'last_comment': last_comment}
			)
			header.is_locked = root.is_locked
			header.last_comment = last_comment
			header.pub_date = root.submit_date
			header.comment_count = statistics['pk__count']
			header.save()

	#def send_notifications(self, sender, instance, created, **kwargs):
	#	if not created:
	#		return
	#	watchers = get_user_model().objects.filter(userdiscussionattribute__discussion = instance.root_header(), userdiscussionattribute__watch = True).distinct()
	#	title = u"Pridaný komentár v diskusii " + unicode(instance.content_object)
	#	author = None
	#	if instance.user:
	#		author = instance.user
	#	Event.objects.broadcast(title, instance.content_object, action = Event.CREATE_ACTION, author = author, users = watchers)
