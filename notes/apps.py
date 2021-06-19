# -*- coding: utf-8 -*-
from django.apps import AppConfig as CoreAppConfig
from django.db.models.signals import post_save


class AppConfig(CoreAppConfig):
	name = 'notes'
	verbose_name = "Poznámky"

	def ready(self):
		Note = self.get_model('Note')
		post_save.connect(self.emit_created, sender=Note)

	def emit_created(self, instance, created, **kwargs):
		from .signals import note_created
		if created:
			note_created.send(
				sender=instance.content_object.__class__,
				instance=instance.content_object, note=instance
			)
