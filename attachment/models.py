# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
import os

class Attachment(models.Model):
	def upload_dir(instance, filename):
		return 'attachment/{0}_{1}/{2}/{3:02x}/{4}'.format(
			instance.content_object._meta.app_label,
			instance.content_object._meta.object_name.lower(),
			instance.content_object.pk,
			instance.content_object.pk,
			filename
		)

	attachment = models.FileField(verbose_name = _('attachment'), upload_to = upload_dir)
	created = models.DateTimeField(auto_now_add = True, verbose_name = _('created'))
	size = models.IntegerField(verbose_name = _('size'))
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey('content_type', 'object_id')

	def delete(self, *args, **kwargs):
		super(Attachment, self).delete(*args, **kwargs)
		self.attachment.storage.delete(self.attachment.path)

	def save(self, *args, **kwargs):
		if self.pk:
			try:
				original = Attachment.objects.get(pk = self.pk)
				if self.attachment != original.attachment:
					original.attachment.storage.delete(original.attachment.path)
			except:
				pass
		self.size = self.attachment.size
		super(Attachment, self).save(*args, **kwargs)

	def clean(self):
		max_size = getattr(settings, 'ATTACHMENT_MAX_SIZE', -1)
		if max_size >= 0 and self.attachment.size > max_size:
			raise ValidationError(_('File size exceeded, maximum size is ') + filesizeformat(max_size))
		db_table = self.content_type.model_class()._meta.db_table
		size_for_content = getattr(settings, 'ATTACHMENT_SIZE_FOR_CONTENT', {}).get(db_table, -1)
		if size_for_content >= 0:
			size = Attachment.objects.filter(object_id = self.object_id, content_type = self.content_type).aggregate(models.Sum('size'))["size__sum"]
			if size is None:
				size = 0
			if self.attachment.size + size > size_for_content:
				raise ValidationError(_('File size for this content exceeded, maximum size is ') + filesizeformat(size_for_content))


	@property
	def name(self):
		return os.path.split(self.attachment.name)[1]

	def __unicode__(self):
		return self.attachment.name

	class Meta:
		verbose_name = _('attachment')
		verbose_name_plural = _('attachments')


class UploadSession(models.Model):
	created = models.DateTimeField(auto_now_add = True)


class TemporaryAttachment(Attachment):
	session = models.ForeignKey(UploadSession)
