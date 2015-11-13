# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


class TimestampModelMixin(models.Model):
	created = models.DateTimeField("vytvorené", editable=False)
	updated = models.DateTimeField("upravené", editable=False)

	def save(self, *args, **kwargs):
		self.updated = timezone.now()
		if not self.id and not self.created:
			self.created = self.updated
		return super(TimestampModelMixin, self).save(*args, **kwargs)

	class Meta:
		abstract = True
