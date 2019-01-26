# -*- coding: utf-8 -*-
from django.db import models

from autoimagefield.fields import AutoImageField


class ImageFieldModel(models.Model):
	image = AutoImageField(upload_to='test/thumbnails', resize_source=dict(size=(64, 64)), blank=True, null=True)

	def __str__(self):
		return self.image.path
