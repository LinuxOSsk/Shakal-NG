# -*- coding: utf-8 -*-
import os

import uuid
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields.files import FileField
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat

from .utils import get_available_size
from common_utils import clean_dir


def upload_to(instance, filename):
	content_class = instance.content_type.model_class()
	return 'attachment/{0}_{1}/{2:02x}/{3}/{4}'.format(
		content_class._meta.app_label,
		content_class._meta.object_name.lower(),
		instance.object_id % 256,
		instance.object_id,
		filename
	)


class AttachmentAbstract(models.Model):
	attachment = FileField(_('attachment'), upload_to=upload_to)
	created = models.DateTimeField(_('created'), auto_now_add=True)
	size = models.IntegerField(_('size'))
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey('content_type', 'object_id')

	class Meta:
		abstract = True

	@property
	def basename(self):
		return os.path.basename(self.attachment.name)

	@property
	def name(self):
		return os.path.split(self.attachment.name)[1]

	@property
	def url(self):
		return settings.MEDIA_URL + self.attachment.name

	@property
	def filename(self):
		return os.path.join(settings.MEDIA_ROOT, self.attachment.name)

	def __unicode__(self):
		return self.attachment.name

	def delete_file(self):
		if self.attachment:
			name = self.attachment.name
			storage = self.attachment.storage
			storage.delete(name)
			clean_dir(os.path.dirname(storage.path(name)), settings.MEDIA_ROOT)
			self.attachment = ''

	def save(self, *args, **kwargs):
		if self.pk:
			original = self.__class__.objects.get(pk = self.pk)
			if self.attachment and original.attachment:
				original.attachment.storage.delete(original.attachment.path)

		self.size = self.attachment.size
		super(AttachmentAbstract, self).save(*args, **kwargs)

	def clean_fields(self, exclude=None):
		uploaded_size = self.__class__.objects \
			.filter(object_id = self.object_id, content_type = self.content_type) \
			.aggregate(models.Sum('size'))["size__sum"]
		available_size = get_available_size(self.content_type, uploaded_size or 0)
		if self.attachment.size > available_size:
			raise ValidationError({'attachment': [_('File size exceeded, maximum size is ') + filesizeformat(available_size)]})
		return super(AttachmentAbstract, self).clean_fields(exclude)


class Attachment(AttachmentAbstract):
	class Meta:
		verbose_name = _('attachment')
		verbose_name_plural = _('attachments')


class UploadSession(models.Model):
	def generate_uuid():
		return uuid.uuid1().hex

	created = models.DateTimeField(auto_now_add=True)
	uuid = models.CharField(max_length=32, unique=True, default=generate_uuid)


class TemporaryAttachment(AttachmentAbstract):
	session = models.ForeignKey(UploadSession)


def delete_file(sender, instance, *args, **kwargs):
	instance.delete_file()
models.signals.pre_delete.connect(delete_file, sender=Attachment)
models.signals.pre_delete.connect(delete_file, sender=TemporaryAttachment)
