# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import pre_delete


class AttachmentConfig(AppConfig):
	name = 'attachment'
	verbose_name = 'Prílohy'

	def delete_file(self, sender, instance, *args, **kwargs): #pylint: disable=unused-argument
		instance.delete_file()

	def ready(self):
		Attachment = self.get_model('Attachment')
		TemporaryAttachment = self.get_model('TemporaryAttachment')

		pre_delete.connect(self.delete_file, sender=Attachment)
		pre_delete.connect(self.delete_file, sender=TemporaryAttachment)
