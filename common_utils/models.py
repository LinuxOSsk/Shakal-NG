# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone


class TimestampModelMixin(models.Model):
	created = models.DateTimeField(
		"vytvorené",
		editable=False
	)
	updated = models.DateTimeField(
		"upravené",
		editable=False
	)

	def save(self, *args, **kwargs):
		self.updated = timezone.now()
		if not self.id and not self.created:
			self.created = self.updated
		return super().save(*args, **kwargs)

	class Meta:
		abstract = True
