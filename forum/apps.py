# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.db.models.signals import post_save


def update_comments_header(sender, instance, **kwargs): #pylint: disable=W0613
	from comments.models import Comment
	from django.contrib.contenttypes.models import ContentType
	from .models import Topic

	root, created = Comment.objects.get_or_create_root_comment(ctype=ContentType.objects.get_for_model(Topic), object_id=instance.pk)
	if created:
		root.last_comment = instance.created
	root.is_removed = instance.is_removed
	root.save()


class ForumConfig(AppConfig):
	name = 'forum'
	verbose_name = 'Fórum'

	def ready(self):
		Topic = self.get_model('Topic')
		post_save.connect(update_comments_header, sender=Topic)
