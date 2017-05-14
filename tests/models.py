# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from autoimagefield.fields import AutoImageField


@python_2_unicode_compatible
class ImageFieldModel(models.Model):
	image = AutoImageField(upload_to='test/thumbnails', resize_source=dict(size=(64, 64)), blank=True, null=True)

	def __str__(self):
		return self.image.path
