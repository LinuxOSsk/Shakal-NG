# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

class Section(models.Model):
	name = models.CharField(max_length = 255, verbose_name = _('name'))
	slug = models.SlugField(unique = True)
	description = models.TextField(verbose_name = _('description'))

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = _('section')
		verbose_name_plural = _('sections')
