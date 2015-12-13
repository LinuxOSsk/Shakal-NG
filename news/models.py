# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import permalink
from django_autoslugfield.fields import AutoSlugField

from attachment.models import Attachment
from comments.models import RootHeader, Comment
from common_utils.models import TimestampModelMixin
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


NEWS_MAX_LENGTH = getattr(settings, 'NEWS_MAX_LENGTH', 3000)


class NewsManager(models.Manager):
	def get_queryset(self):
		return super(NewsManager, self).get_queryset().select_related('author')


class NewsListManager(models.Manager):
	def get_queryset(self):
		return super(NewsListManager, self).get_queryset().select_related('author').filter(approved=True).order_by('-pk')


class News(TimestampModelMixin, models.Model):
	all_news = NewsManager()
	objects = NewsListManager()

	title = models.CharField(max_length=255, verbose_name='titulok')
	slug = AutoSlugField(title_field="title", unique=True)
	original_short_text = RichTextOriginalField(filtered_field="filtered_short_text", property_name="short_text", verbose_name='krátky text', max_length=NEWS_MAX_LENGTH)
	filtered_short_text = RichTextFilteredField()
	original_long_text = RichTextOriginalField(filtered_field="filtered_long_text", property_name="long_text", verbose_name='dlhý text')
	filtered_long_text = RichTextFilteredField()
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='author')
	authors_name = models.CharField(max_length=255, verbose_name='meno authora')
	source = models.CharField(max_length=100, verbose_name='zdroj', blank=True)
	source_url = models.URLField(max_length=1000, verbose_name='URL zdroja', blank=True)
	approved = models.BooleanField(default=False, verbose_name='schválená')
	comments_header = GenericRelation(RootHeader)
	attachments = GenericRelation(Attachment)
	comments = GenericRelation(Comment)

	content_fields = ('original_short_text', 'original_long_text',)

	class Meta:
		verbose_name = 'správa'
		verbose_name_plural = 'správy'

	@permalink
	def get_absolute_url(self):
		return ('news:detail-by-slug', None, {'slug': self.slug})

	@permalink
	def get_list_url(self):
		return ('news:list', None, None)

	def __unicode__(self):
		return self.title
