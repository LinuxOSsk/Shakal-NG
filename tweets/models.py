# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django_autoslugfield.fields import AutoSlugField

from comments.models import RootHeader, Comment
from common_utils.models import TimestampModelMixin
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


TWEET_MAX_LENGTH = getattr(settings, 'TWEET_MAX_LENGTH', 400)


class Tweet(TimestampModelMixin, models.Model):
	title = models.CharField(
		max_length=255,
		verbose_name='titulok'
	)
	slug = AutoSlugField(
		title_field='title',
		unique=True
	)

	original_text = RichTextOriginalField(
		filtered_field='filtered_text',
		property_name='text',
		verbose_name='text',
		max_length=TWEET_MAX_LENGTH
	)
	filtered_text = RichTextFilteredField()


	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		verbose_name='autor'
	)

	link_text = models.CharField(
		max_length=100,
		verbose_name='text odkazu',
		blank=True
	)
	link_url = models.URLField(
		max_length=1000,
		verbose_name='odkaz',
		blank=True
	)

	comments_header = GenericRelation(RootHeader)
	comments = GenericRelation(Comment)

	content_fields = ('original_text',)

	class Meta:
		verbose_name = 'tweet'
		verbose_name_plural = 'tweety'

	def get_absolute_url(self):
		return reverse('tweets:detail', kwargs={'slug': self.slug})

	def get_list_url(self):
		return reverse('tweets:list', kwargs={'page': 1})

	def __str__(self):
		return self.title
