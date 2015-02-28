# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import pre_delete, pre_save, post_save


class AttachmentConfig(AppConfig):
	name = 'attachment'
	verbose_name = 'Prílohy'

	def delete_file(self, sender, instance, *args, **kwargs): #pylint: disable=unused-argument
		instance.delete_file()

	def delete_attachmentimage(self, sender, instance, *args, **kwargs): #pylint: disable=unused-argument
		AttachmentImageRaw = self.get_model('AttachmentImageRaw')
		for obj in list(AttachmentImageRaw.objects.all().filter(attachment_ptr=instance.pk)):
			obj.delete()

	def create_attachmentimage(self, sender, instance, *args, **kwargs): #pylint: disable=unused-argument
		try:
			AttachmentImageRaw = self.get_model('AttachmentImageRaw')
			from PIL import Image
			img = Image.open(instance.attachment.storage.path(instance.attachment.name))
			width, height = img.size
			AttachmentImageRaw.objects.get_or_create(attachment_ptr=instance.pk, width=width, height=height)
		except Exception:
			pass

	def ready(self):
		Attachment = self.get_model('Attachment')
		TemporaryAttachment = self.get_model('TemporaryAttachment')

		pre_delete.connect(self.delete_file, sender=Attachment)
		pre_delete.connect(self.delete_file, sender=TemporaryAttachment)
		pre_delete.connect(self.delete_attachmentimage, sender=Attachment)
		pre_save.connect(self.delete_attachmentimage, sender=Attachment)
		post_save.connect(self.create_attachmentimage, sender=Attachment)
