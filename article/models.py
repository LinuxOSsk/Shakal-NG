# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import permalink
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.functional import cached_property
from django.utils.timezone import now

from attachment.models import Attachment
from autoimagefield.fields import AutoImageField
from comments.models import RootHeader, Comment
from common_utils.models import TimestampModelMixin
from common_utils.related_documents import related_documents
from hitcount.models import HitCountField
from polls.models import Poll
from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


@python_2_unicode_compatible
class Category(models.Model):
	name = models.CharField('názov', max_length=255)
	slug = models.SlugField('skratka URL', unique=True)
	description = models.TextField('popis')

	@permalink
	def get_absolute_url(self):
		return ('article:list-category', None, {'category': self.slug})

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = 'kategória'
		verbose_name_plural = 'kategórie'


class ArticleManager(models.Manager):
	def get_queryset(self):
		return (super(ArticleManager, self).get_queryset()
			.filter(published=True)
			.filter(pub_time__lte=now())
			.order_by('-pub_time', '-pk'))


@python_2_unicode_compatible
class Article(TimestampModelMixin, models.Model):
	all_articles = models.Manager()
	objects = ArticleManager()

	title = models.CharField('názov', max_length=255)
	slug = models.SlugField('skratka URL', unique=True)
	category = models.ForeignKey(Category, verbose_name='kategória', on_delete=models.PROTECT)

	original_perex = RichTextOriginalField(
		filtered_field='filtered_perex',
		property_name='perex',
		verbose_name='text na titulnej stránke',
		parsers={'raw': ''}
	)
	filtered_perex = RichTextFilteredField()

	original_annotation = RichTextOriginalField(
		filtered_field='filtered_annotation',
		property_name='annotation',
		verbose_name='text pred telom článku',
		parsers={'raw': ''}
	)
	filtered_annotation = RichTextFilteredField()

	original_content = RichTextOriginalField(
		filtered_field='filtered_content',
		property_name='content',
		verbose_name='obsah',
		parsers={'raw': ''}
	)
	filtered_content = RichTextFilteredField()

	author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='autor', on_delete=models.SET_NULL, blank=True, null=True)
	authors_name = models.CharField('meno autora', max_length=255)
	pub_time = models.DateTimeField('čas publikácie', default=now, db_index=True)
	published = models.BooleanField('publikované', default=False)
	top = models.BooleanField('hodnotný článok', default=False)
	image = AutoImageField('obrázok', upload_to='article/thumbnails', resize_source=dict(size=(2048, 2048)), blank=True)
	polls = GenericRelation(Poll)
	comments_header = GenericRelation(RootHeader)
	comments = GenericRelation(Comment)
	attachments = GenericRelation(Attachment)
	hit = HitCountField()

	content_fields = ('original_perex', 'original_annotation', 'original_content',)

	@property
	def poll_set(self):
		return self.polls.all().filter(approved=True).order_by('pk').all()

	@permalink
	def get_absolute_url(self):
		return ('article:detail', None, {'slug': self.slug})

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
		verbose_name = 'článok'
		verbose_name_plural = 'články'


@python_2_unicode_compatible
class Series(TimestampModelMixin, models.Model):
	name = models.CharField('názov seriálu', max_length=100)
	slug = models.SlugField('skratka URL', unique=True)
	image = AutoImageField('obrázok', upload_to='article/thumbnails', resize_source=dict(size=(2048, 2048)), blank=True)
	description = models.TextField('popis')

	@permalink
	def get_absolute_url(self):
		return ('article:list-series', None, {'category': self.slug})

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = 'seriál'
		verbose_name_plural = 'seriály'


@python_2_unicode_compatible
class SeriesArticle(models.Model):
	article = models.OneToOneField(Article, verbose_name='článok', related_name='series')
	series = models.ForeignKey(Series, verbose_name='seriál')

	def __str__(self, *args, **kwargs):
		return force_text(self.series) + ' / ' + force_text(self.article)

	class Meta:
		verbose_name = 'seriálový článok'
		verbose_name_plural = 'seriálové články'
		ordering = ('pk',)
