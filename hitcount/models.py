# -*- coding: utf-8 -*-
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models


class HitCount(models.Model):
	hits = models.PositiveIntegerField(default = 0)
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	content_object = generic.GenericForeignKey('content_type', 'object_id')

	def __unicode__(self):
		return unicode(self.content_type) + '/' + unicode(self.content_object)

	class Meta:
		unique_together = (('content_type', 'object_id'),)


class HitCountField(models.Field):
	def db_type(self):
		return None

	@staticmethod
	def get_hit_count(cls, pk):
		content_type = ContentType.objects.get_for_model(cls)
		hit_count, created = HitCount.objects.get_or_create(content_type = content_type, object_id = pk)
		return hit_count

	def contribute_to_class(self, cls, name):
		def hit(self):
			hit_count = HitCountField.get_hit_count(self.__class__, self.pk)
			hit_count.hits += 1
			hit_count.save()
		hit.alters_data = True
		setattr(cls, name, hit)

		def hit_count(self):
			if not self.pk:
				return 0
			hit_count = HitCountField.get_hit_count(self.__class__, self.pk)
			return hit_count.hits
		setattr(cls, name + '_count', property(hit_count))
