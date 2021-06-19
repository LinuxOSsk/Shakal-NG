# -*- coding: utf-8 -*-
from django.apps import AppConfig

from common_utils.mail import send_template_mail
from notes.signals import note_created


class NewsConfig(AppConfig):
	name = 'news'
	verbose_name = 'Správy'

	def ready(self):
		News = self.get_model('News')
		note_created.connect(self.note_created, sender=News)

	def note_created(self, instance, note, **kwargs):
		from django.contrib.auth import get_user_model
		from notifications.models import Event

		if not instance.author or not instance.author.email:
			return
		ctx = {
			'news': instance,
			'note': note,
		}
		send_template_mail(template_base='news/email/note_created', context=ctx, to=[instance.author.email])
		title = 'K správe ' + instance.title + ' bola pridaná poznámka'
		Event.objects.broadcast(
			title,
			instance,
			author=note.author,
			action=Event.MESSAGE_ACTION,
			users=get_user_model().objects.filter(pk=instance.author.pk)
		)
