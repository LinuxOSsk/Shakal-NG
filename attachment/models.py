# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
import os

class Attachment(models.Model):
	def upload_dir(instance, filename):
		return 'attachment/{0}_{1}/{2}/{3}'.format(
			instance.content_object._meta.app_label,
			instance.content_object._meta.object_name.lower(),
			instance.content_object.pk,
			filename
		)

	attachment = models.FileField(verbose_name = _('attachment'), upload_to = upload_dir)
	created = models.DateTimeField(auto_now_add = True, verbose_name = _('created'))
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey('content_type', 'object_id')

	def delete(self, *args, **kwargs):
		super(Attachment, self).delete(*args, **kwargs)
		self.attachment.storage.delete(self.attachment.path)

	@property
	def name(self):
		return os.path.split(self.attachment.name)[1]

	def __unicode__(self):
		return self.attachment.name
