# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible

from common_utils.models import TimestampModelMixin
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


@python_2_unicode_compatible
class Note(TimestampModelMixin, models.Model):
	content_type = models.ForeignKey(
		ContentType,
		limit_choices_to = (
			Q(app_label='news', model='news')
		),
		verbose_name='typ obsahu',
		on_delete=models.PROTECT
	)
	object_id = models.PositiveIntegerField(
		verbose_name='id objektu',
	)
	content_object = GenericForeignKey('content_type', 'object_id')

	subject = models.CharField('predmet', max_length=100)

	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		blank=True,
		null=True,
		verbose_name='autor',
		on_delete=models.SET_NULL
	)
	authors_name = models.CharField(
		max_length=255,
		verbose_name='meno autora'
	)

	original_text = RichTextOriginalField(
		filtered_field='filtered_text',
		property_name='text',
		verbose_name='poznámka',
		max_length=20000
	)
	filtered_text = RichTextFilteredField()

	def __str__(self):
		return self.subject
		#return Truncator(strip_tags(self.filtered_text).replace('&shy;', '')).words(3, truncate="...")

	class Meta:
		verbose_name = 'poznámka'
		verbose_name_plural = 'poznámky'
