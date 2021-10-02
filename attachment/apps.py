# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.db.models.signals import pre_delete, pre_save, post_save


class AttachmentConfig(AppConfig):
	name = 'attachment'
	verbose_name = 'Prílohy'

	def delete_file(self, sender, instance, *args, **kwargs): #pylint: disable=unused-argument
		instance.delete_file()

	def delete_attachmentimage(self, sender, instance, *args, **kwargs): #pylint: disable=unused-argument
		AttachmentImage = self.get_model('AttachmentImage')
		for obj in list(AttachmentImage.objects.all().filter(attachment_ptr=instance.pk)):
			obj.delete(keep_parents=True)

	def create_attachmentimage(self, sender, instance, *args, **kwargs): #pylint: disable=unused-argument
		try:
			AttachmentImageRaw = self.get_model('AttachmentImageRaw')
			from PIL import Image
			img = Image.open(instance.attachment.storage.path(instance.attachment.name))
			width, height = img.size
			if width > 8192 or height > 8192:
				return
			if (width * height) > (1024 * 1024 * 32):
				return
			AttachmentImageRaw.objects.get_or_create(attachment_ptr=instance.pk, width=width, height=height)
		except Exception: #pylint: disable=broad-except
			pass

	def ready(self):
		Attachment = self.get_model('Attachment')

		pre_delete.connect(self.delete_file, sender=Attachment)
		pre_delete.connect(self.delete_attachmentimage, sender=Attachment)
		pre_save.connect(self.delete_attachmentimage, sender=Attachment)
		post_save.connect(self.create_attachmentimage, sender=Attachment)
