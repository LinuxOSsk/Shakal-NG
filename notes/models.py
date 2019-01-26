# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q

from common_utils.models import TimestampModelMixin
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


class Note(TimestampModelMixin, models.Model):
	content_type = models.ForeignKey(
		ContentType,
		verbose_name="typ obsahu",
		limit_choices_to = (
			Q(app_label='news', model='news') |
			Q(app_label='comments', model='comment') |
			Q(app_label='forum', model='topic')
		),
		on_delete=models.PROTECT
	)
	object_id = models.PositiveIntegerField(
		verbose_name="id objektu",
	)
	content_object = GenericForeignKey('content_type', 'object_id')

	subject = models.CharField(
		"predmet",
		max_length=100,
		blank=True
	)

	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name="autor",
		blank=True,
		null=True,
		on_delete=models.SET_NULL
	)
	authors_name = models.CharField(
		verbose_name="meno autora",
		max_length=255
	)

	original_text = RichTextOriginalField(
		verbose_name="poznámka",
		filtered_field='filtered_text',
		property_name='text',
		max_length=20000
	)
	filtered_text = RichTextFilteredField()

	is_public = models.BooleanField(
		verbose_name="poznámka je verejná",
		help_text="Poznámku môže vidieť ktorýkoľvek návštevník",
		blank=True,
		default=False,
	)

	def __str__(self):
		return self.subject

	class Meta:
		verbose_name = "poznámka"
		verbose_name_plural = "poznámky"
