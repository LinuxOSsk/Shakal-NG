# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.timezone import now

from autoimagefield.fields import AutoImageField
from common_utils.models import TimestampModelMixin
from common_utils.related_documents import related_documents
from hitcount.models import HitCountField
from linuxos.model_fields import PresentationImageField
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


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
	image = AutoImageField(
		verbose_name="obrázok",
		upload_to='article/categories',
		blank=True
	)

	def get_absolute_url(self):
		return reverse('article:list-category', kwargs={'category': self.slug, 'page': 1})

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "kategória"
		verbose_name_plural = "kategórie"


class ArticleManager(models.Manager):
	def get_queryset(self):
		return (super().get_queryset()
			.filter(published=True)
			.filter(pub_time__lte=now())
			.order_by('-pub_time', '-pk'))


class Article(TimestampModelMixin, models.Model):
	all_articles = models.Manager()
	objects = ArticleManager()

	title = models.CharField(
		verbose_name="názov",
		max_length=255
	)
	slug = models.SlugField(
		verbose_name="skratka URL",
		unique=True
	)
	category = models.ForeignKey(
		Category,
		verbose_name="kategória",
		on_delete=models.PROTECT
	)

	original_perex = RichTextOriginalField(
		verbose_name="text na titulnej stránke",
		filtered_field='filtered_perex',
		property_name='perex',
		parsers={'raw': ''}
	)
	filtered_perex = RichTextFilteredField(
	)

	original_annotation = RichTextOriginalField(
		verbose_name="text pred telom článku",
		filtered_field='filtered_annotation',
		property_name='annotation',
		parsers={'raw': ''}
	)
	filtered_annotation = RichTextFilteredField(
	)

	original_content = RichTextOriginalField(
		verbose_name="obsah",
		filtered_field='filtered_content',
		property_name='content',
		parsers={'raw': ''}
	)
	filtered_content = RichTextFilteredField(
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
	pub_time = models.DateTimeField(
		verbose_name="čas publikácie",
		default=now,
		db_index=True
	)
	published = models.BooleanField(
		verbose_name="publikované",
		default=False
	)
	top = models.BooleanField(
		verbose_name="hodnotný článok",
		default=False
	)
	image = AutoImageField(
		verbose_name="obrázok",
		upload_to='article/thumbnails',
		blank=True
	)

	presentation_image = PresentationImageField(verbose_name="prezentačný obrázok")
	polls = GenericRelation('polls.Poll')
	comments_header = GenericRelation('comments.RootHeader')
	comments = GenericRelation('comments.Comment')
	attachments = GenericRelation('attachment.Attachment')
	hit = HitCountField()

	content_fields = ('original_perex', 'original_annotation', 'original_content',)

	@property
	def poll_set(self):
		return self.polls.all().filter(approved=True).order_by('pk').all()

	def get_absolute_url(self):
		return reverse('article:detail', kwargs={'slug': self.slug})

	@cached_property
	def series_object(self):
		if hasattr(self, 'series'):
			return self.series.series
		else:
			return None

	@cached_property
	def related_documents(self):
		series = self.series_object
		if not series:
			return None
		articles = Article.objects.filter(series__series=series)
		related = related_documents(
			instance=self,
			queryset=articles.only('pk', 'series__id', 'title', 'slug'),
			ordering=['series__id'],
			select_range=3
		)
		related['up'] = series
		return related

	def is_published(self):
		return self.published and self.pub_time <= now()

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = "článok"
		verbose_name_plural = "články"


class Series(TimestampModelMixin, models.Model):
	name = models.CharField(
		verbose_name="názov seriálu",
		max_length=100
	)
	slug = models.SlugField(
		verbose_name="skratka URL",
		unique=True
	)
	image = AutoImageField(
		verbose_name="obrázok",
		upload_to='article/thumbnails',
		resize_source=dict(size=(2048, 2048)),
		blank=True
	)
	description = models.TextField(
		verbose_name="popis"
	)

	def get_absolute_url(self):
		return reverse('article:list-series', kwargs={'category': self.slug, 'page': 1})

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "seriál"
		verbose_name_plural = "seriály"


class SeriesArticle(models.Model):
	article = models.OneToOneField(
		Article,
		verbose_name="článok",
		related_name='series',
		on_delete=models.CASCADE
	)
	series = models.ForeignKey(
		Series,
		verbose_name="seriál",
		on_delete=models.CASCADE
	)

	def __str__(self, *args, **kwargs):
		return '%s / %s' % (self.series, self.article)

	class Meta:
		verbose_name = "seriálový článok"
		verbose_name_plural = "seriálové články"
		ordering = ('pk',)
