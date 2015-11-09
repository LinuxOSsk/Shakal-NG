# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import permalink
from django.utils.timezone import now

from attachment.models import Attachment
from autoimagefield.fields import AutoImageField
from common_utils.models import TimestampModelMixin
from hitcount.models import HitCountField
from polls.models import Poll
from threaded_comments.models import RootHeader, Comment


class Category(models.Model):
	name = models.CharField('názov', max_length=255)
	slug = models.SlugField('skratka URL', unique=True)
	description = models.TextField('popis')

	@permalink
	def get_absolute_url(self):
		return ('article:list-category', None, {'category': self.slug})

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = 'kategória'
		verbose_name_plural = 'kategórie'


class ArticleManager(models.Manager):
	def get_queryset(self):
		return super(ArticleManager, self).get_queryset() \
			.filter(published=True) \
			.filter(pub_time__lte=now()) \
			.order_by('-pk')


class Article(TimestampModelMixin, models.Model):
	all_articles = models.Manager()
	objects = ArticleManager()

	title = models.CharField('názov', max_length=255)
	slug = models.SlugField('skratka URL', unique=True)
	category = models.ForeignKey(Category, verbose_name='kategória', on_delete=models.PROTECT)
	perex = models.TextField('perex', help_text='Text na titulnej stránke')
	annotation = models.TextField('anotácia', help_text='Text pred telom článku')
	content = models.TextField('obsah')
	author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='autor', on_delete=models.SET_NULL, blank=True, null=True)
	authors_name = models.CharField('meno autora', max_length=255)
	pub_time = models.DateTimeField('čas publikácie', default=now)
	published = models.BooleanField('publikované', default=False)
	top = models.BooleanField('hodnotný článok', default=False)
	image = AutoImageField('obrázok', upload_to='article/thumbnails', size=(512, 512), thumbnail={'standard': (100, 100)}, blank=True, null=True)
	polls = GenericRelation(Poll)
	comments_header = GenericRelation(RootHeader)
	comments = GenericRelation(Comment)
	attachments = GenericRelation(Attachment)
	hit = HitCountField()

	@property
	def poll_set(self):
		return self.polls.filter(approved=True).order_by('pk').all()

	def clean_fields(self, exclude=None):
		slug_num = None
		try:
			slug_num = int(self.slug)
		except ValueError:
			pass
		if slug_num is not None:
			raise ValidationError({'slug': ['Číselné slugy nie sú povolené']})
		super(Article, self).clean_fields(exclude)

	@permalink
	def get_absolute_url(self):
		return ('article:detail', None, {'slug': self.slug})

	def is_published(self):
		return self.published and self.pub_time <= now()

	def __unicode__(self):
		return self.title

	class Meta:
		verbose_name = 'článok'
		verbose_name_plural = 'články'
