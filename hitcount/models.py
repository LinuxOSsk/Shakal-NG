# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class HitCount(models.Model):
	hits = models.PositiveIntegerField(default = 0)
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey('content_type', 'object_id')

	def __unicode__(self):
		return unicode(self.content_type) + '/' + unicode(self.content_object)

	class Meta:
		unique_together = (('content_type', 'object_id'),)
