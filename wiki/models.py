# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mptt
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django_autoslugfield.fields import AutoSlugField

from common_utils.models import TimestampModelMixin
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


@python_2_unicode_compatible
class Page(mptt.models.MPTTModel, TimestampModelMixin):
	TYPE_CHOICES = (
		('h', 'Domovská stránka'),
		('i', 'Interná stránka'),
		('p', 'Stránka wiki'),
	)

	title = models.CharField('titulok', max_length=255)
	last_author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='posledný autor', blank=True, null=True, on_delete=models.SET_NULL)
	slug = AutoSlugField(unique=True, verbose_name='slug', title_field='title')
	parent = models.ForeignKey('self', related_name='children', blank=True, null=True, verbose_name='nadradená stránka', on_delete=models.PROTECT)
	original_text = RichTextOriginalField(filtered_field="filtered_text", property_name="text", verbose_name="text")
	filtered_text = RichTextFilteredField()
	page_type = models.CharField('typ stránky', max_length=1, choices=TYPE_CHOICES, default='p')

	content_fields = ('original_text',)

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = 'Wiki stránka'
		verbose_name_plural = 'Wiki stránky'

	def get_absolute_url(self):
		if self.page_type == 'h' and not self.parent:
			return reverse('wiki:home')
		else:
			return reverse('wiki:page', kwargs={'slug': self.slug, 'page': 1})
