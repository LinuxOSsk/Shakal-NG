# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from common_utils import clean_dir
import uuid
import os

class AttachmentAbstract(models.Model):
	def upload_to(instance, filename):
		content_class = instance.content_type.model_class()
		return 'attachment/{0}_{1}/{2:02x}/{3}/{4}'.format(
			content_class._meta.app_label,
			content_class._meta.object_name.lower(),
			instance.object_id % 256,
			instance.object_id,
			filename
		)

	attachment = models.FileField(verbose_name = _('attachment'), upload_to = upload_to)
	created = models.DateTimeField(auto_now_add = True, verbose_name = _('created'))
	size = models.IntegerField(verbose_name = _('size'))
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey('content_type', 'object_id')

	def basename(self):
		return os.path.basename(self.attachment.name)

	def delete(self, *args, **kwargs):
		path = self.attachment.storage.path(self.attachment.name)
		super(AttachmentAbstract, self).delete(*args, **kwargs)
		self.attachment.storage.delete(self.attachment.path)
		clean_dir(os.path.dirname(path), settings.MEDIA_ROOT)

	def save(self, *args, **kwargs):
		if self.pk:
			try:
				original = Attachment.objects.get(pk = self.pk)
				if self.attachment != original.attachment:
					original.attachment.storage.delete(original.attachment.path)
			except:
				pass
		self.size = self.attachment.size
		target_name = self.upload_to(os.path.basename(self.attachment.name))
		if target_name != self.attachment.name:
			if self.attachment.storage.exists(self.attachment.name):
				file_name = self.attachment.storage.save(self.upload_to(os.path.basename(self.attachment.name)), self.attachment.file)
				self.attachment = file_name
		super(AttachmentAbstract, self).save(*args, **kwargs)

	def clean(self):
		available_size = self.get_available_size(self.content_type, class_instance = self.__class__.objects.filter(object_id = self.object_id, content_type = self.content_type).aggregate(models.Sum('size'))["size__sum"])
		if self.attachment.size > available_size:
			raise ValidationError(_('File size exceeded, maximum size is ') + filesizeformat(available_size))

	@staticmethod
	def get_available_size(content_type, uploaded_size):
		if isinstance(content_type, (int, long, str, unicode)):
			content_type = ContentType.objects.get(pk = int(content_type))
		max_size = getattr(settings, 'ATTACHMENT_MAX_SIZE', -1)
		db_table = content_type.model_class()._meta.db_table
		size_for_content = getattr(settings, 'ATTACHMENT_SIZE_FOR_CONTENT', {}).get(db_table, -1)
		# Bez limitu
		if max_size < 0 and size_for_content < 0:
			return -1
		# Obsah bez limitu
		if size_for_content < 0:
			return max_size
		if max_size < 0:
			return max(size_for_content - uploaded_size, 0)
		else:
			return max(min(max_size, size_for_content - uploaded_size), 0)

	@property
	def name(self):
		return os.path.split(self.attachment.name)[1]

	def __unicode__(self):
		return self.attachment.name

	class Meta:
		abstract = True


class Attachment(AttachmentAbstract):
	class Meta:
		verbose_name = _('attachment')
		verbose_name_plural = _('attachments')


def generate_uuid():
	return uuid.uuid1().hex

class UploadSession(models.Model):
	created = models.DateTimeField(auto_now_add = True)
	uuid = models.CharField(max_length = 32, unique = True, default = generate_uuid)


class TemporaryAttachment(AttachmentAbstract):
	session = models.ForeignKey(UploadSession)
