# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding  import python_2_unicode_compatible, force_text

from .cache import cache


@python_2_unicode_compatible
class HitCount(models.Model):
	hits = models.PositiveIntegerField(default=0)
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')

	def __str__(self):
		return force_text(self.content_type) + '/' + force_text(self.content_object)

	class Meta:
		unique_together = (('content_type', 'object_id'),)


class HitCountField(models.Field):
	def db_type(self, *args, **kwargs): # virtual field
		return None

	@staticmethod
	def get_hit_count(model_class, pk):
		content_type = ContentType.objects.get_for_model(model_class)
		hit_count = HitCount.objects.get_or_create(content_type=content_type, object_id=pk)[0]
		return hit_count

	def contribute_to_class(self, cls, name, **kwargs):
		def hit(self):
			hit_count = HitCountField.get_hit_count(self.__class__, self.pk)
			hit_count.hits += 1
			hit_count.save()
			cache.set_hitcount(hit_count.object_id, hit_count.content_type_id, hit_count.hits)
		hit.alters_data = True
		setattr(cls, name, hit)

		def hit_count(self):
			if not self.pk:
				return 0
			hit_count = HitCountField.get_hit_count(self.__class__, self.pk)
			return hit_count.hits
		setattr(cls, name + '_count', property(hit_count))
