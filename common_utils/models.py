# -*- coding: utf-8 -*-
from django.core.management.color import no_style
from django.db import models, connection
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


def sql_sequence_reset(model_classes):
	statements = connection.ops.sequence_reset_sql(no_style(), model_classes)
	for statement in statements:
		with connection.cursor() as c:
			try:
				c.execute(statement)
			finally:
				c.close()
