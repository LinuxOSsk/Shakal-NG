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


class Category(models.Model):
	name = models.CharField('názov', max_length=255)
	slug = models.SlugField(unique=True)
	description = models.TextField('popis')

	@models.permalink
	def get_absolute_url(self):
		return ('news:list-category', None, {'category': self.slug})

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = 'kategória'
		verbose_name_plural = 'kategórie'


class News(TimestampModelMixin, models.Model):
	all_news = NewsManager()
	objects = NewsListManager()

	title = models.CharField(max_length=255, verbose_name='titulok')
	slug = AutoSlugField(title_field='title', unique=True)
	category = models.ForeignKey(Category, verbose_name='kategória', on_delete=models.PROTECT)

	original_short_text = RichTextOriginalField(
		filtered_field='filtered_short_text',
		property_name='short_text',
		verbose_name='krátky text',
		parsers={'html': 'news_short'},
		max_length=NEWS_MAX_LENGTH
	)
	filtered_short_text = RichTextFilteredField()

	original_long_text = RichTextOriginalField(
		filtered_field='filtered_long_text',
		property_name='long_text',
		verbose_name='dlhý text',
		parsers={'html': 'news_long'},
		help_text='Vyplňte v prípade, že sa text v detaile správy má líšiť od textu v zozname.'
	)
	filtered_long_text = RichTextFilteredField()

	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='autor')
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
		return ('news:detail', None, {'slug': self.slug})

	@permalink
	def get_list_url(self):
		return ('news:list', None, None)

	def __unicode__(self):
		return self.title
