# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django_autoslugfield.fields import AutoSlugField

from common_utils.models import TimestampModelMixin
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


TWEET_MAX_LENGTH = getattr(settings, 'TWEET_MAX_LENGTH', 400)


class Tweet(TimestampModelMixin, models.Model):
	title = models.CharField(
		verbose_name="titulok",
		max_length=255
	)
	slug = AutoSlugField(
		verbose_name="skratka URL",
		title_field='title',
		unique=True
	)

	original_text = RichTextOriginalField(
		verbose_name="text",
		filtered_field='filtered_text',
		property_name='text',
		max_length=TWEET_MAX_LENGTH
	)
	filtered_text = RichTextFilteredField()


	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name="autor",
		on_delete=models.CASCADE
	)

	link_text = models.CharField(
		verbose_name="text odkazu",
		max_length=100,
		blank=True
	)
	link_url = models.URLField(
		verbose_name="odkaz",
		max_length=1000,
		blank=True
	)

	comments_header = GenericRelation('comments.RootHeader')
	comments = GenericRelation('comments.Comment')

	content_fields = ('original_text',)

	class Meta:
		verbose_name = "tweet"
		verbose_name_plural = "tweety"

	def get_absolute_url(self):
		return reverse('tweets:detail', kwargs={'slug': self.slug})

	def get_list_url(self):
		return reverse('tweets:list', kwargs={'page': 1})

	def __str__(self):
		return self.title
