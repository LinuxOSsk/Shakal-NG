# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from autoimagefield.fields import AutoImageField


class ImageFieldModel(models.Model):
	image = AutoImageField(upload_to='test/thumbnails', resize_source=dict(size=(64, 64)), blank=True, null=True)

	def __unicode__(self):
		return self.image.path
