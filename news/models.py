# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django_autoslugfield.fields import AutoSlugField

from common_utils.models import TimestampModelMixin
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


NEWS_MAX_LENGTH = getattr(settings, 'NEWS_MAX_LENGTH', 3000)


class Category(models.Model):
	name = models.CharField(
		verbose_name="názov",
		max_length=255
	)
	slug = models.SlugField(
		verbose_name="skratka URL",
		unique=True
	)
	description = models.TextField(
		verbose_name="popis"
	)

	def get_absolute_url(self):
		return reverse('news:list-category', kwargs={'category': self.slug, 'page': 1})

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "kategória"
		verbose_name_plural = "kategórie"


class NewsManager(models.Manager):
	def get_queryset(self):
		return (super().get_queryset()
			.select_related('author'))


class NewsListManager(models.Manager):
	def get_queryset(self):
		return (super().get_queryset()
			.select_related('author')
			.filter(approved=True)
			.order_by('-pk'))


class News(TimestampModelMixin, models.Model):
	all_news = NewsManager()
	objects = NewsListManager()

	title = models.CharField(
		verbose_name="titulok",
		max_length=255
	)
	slug = AutoSlugField(
		verbose_name="skratka URL",
		title_field='title',
		unique=True
	)
	category = models.ForeignKey(
		Category,
		verbose_name="kategória",
		on_delete=models.PROTECT
	)

	original_short_text = RichTextOriginalField(
		verbose_name="krátky text",
		filtered_field='filtered_short_text',
		property_name='short_text',
		parsers={'html': 'news_short'},
		max_length=NEWS_MAX_LENGTH
	)
	filtered_short_text = RichTextFilteredField(
	)

	original_long_text = RichTextOriginalField(
		verbose_name="dlhý text",
		filtered_field='filtered_long_text',
		property_name='long_text',
		parsers={'html': 'news_long'},
		help_text="Vyplňte v prípade, že sa text v detaile správy má líšiť od textu v zozname."
	)
	filtered_long_text = RichTextFilteredField(
	)

	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name="autor",
		on_delete=models.SET_NULL,
		blank=True,
		null=True
	)
	authors_name = models.CharField(
		verbose_name="meno autora",
		max_length=255
	)
	source = models.CharField(
		verbose_name="zdroj",
		max_length=100,
		blank=True
	)
	source_url = models.URLField(
		verbose_name="URL zdroja",
		max_length=1000,
		blank=True
	)
	approved = models.BooleanField(
		verbose_name="schválená",
		default=False
	)
	event_date = models.DateField(
		verbose_name="dátum udalosti",
		help_text="Pri vyplnení sa správička zobrazí v kalendári udalostí.",
		blank=True,
		null=True
	)

	comments_header = GenericRelation('comments.RootHeader')
	comments = GenericRelation('comments.Comment')
	attachments = GenericRelation('attachment.Attachment')
	notes = GenericRelation('notes.Note')

	content_fields = ('original_short_text', 'original_long_text',)

	class Meta:
		verbose_name = "správa"
		verbose_name_plural = "správy"

	def get_absolute_url(self):
		return reverse('news:detail', kwargs={'slug': self.slug})

	def get_list_url(self):
		return reverse('news:list', kwargs={'page': 1})

	@cached_property
	def admin_notes(self):
		return self.notes.order_by('pk')

	@cached_property
	def public_notes(self):
		return self.admin_notes.filter(is_public=True)

	def __str__(self):
		return self.title
