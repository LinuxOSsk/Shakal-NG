# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import permalink
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from attachment.models import Attachment
from autoimagefield.fields import AutoImageField
from hitcount.models import HitCountField
from polls.models import Poll
from threaded_comments.models import RootHeader, Comment


class Category(models.Model):
	name = models.CharField(_('name'), max_length = 255)
	slug = models.SlugField(unique = True)
	description = models.TextField(_('description'))

	@permalink
	def get_absolute_url(self):
		return ('article:list-category', None, {'category': self.slug})

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = _('category')
		verbose_name_plural = _('categories')


class ArticleManager(models.Manager):
	def get_query_set(self):
		return super(ArticleManager, self).get_query_set() \
			.filter(published = True) \
			.filter(pub_time__lte = now()) \
			.order_by('-pk')


class Article(models.Model):
	all_articles = models.Manager()
	objects = ArticleManager()

	title = models.CharField(_('title'), max_length = 255)
	slug = models.SlugField(unique = True)
	category = models.ForeignKey(Category, verbose_name = _('category'), on_delete = models.PROTECT)
	perex = models.TextField(_('perex'), help_text = _('Text on title page.'))
	annotation = models.TextField(_('annotation'), help_text = _('Text before article body.'))
	content = models.TextField(_('content'))
	author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name = _('author'), on_delete = models.SET_NULL, blank = True, null = True)
	authors_name = models.CharField(_('authors name'), max_length = 255)
	pub_time = models.DateTimeField(_('publication time'), default = now)
	updated = models.DateTimeField(editable = False)
	published = models.BooleanField(_('published'))
	top = models.BooleanField(_('top article'))
	image = AutoImageField(_('image'), upload_to = 'article/thumbnails', size = (512, 512), thumbnail = {'standard': (100, 100)}, blank = True, null = True)
	polls = generic.GenericRelation(Poll)
	comments_header = generic.GenericRelation(RootHeader)
	comments = generic.GenericRelation(Comment)
	attachments = generic.GenericRelation(Attachment)
	hit = HitCountField()

	def save(self, *args, **kwargs):
		self.updated = now()
		if not self.id and not self.pub_time:
			self.pub_time = self.updated
		return super(Article, self).save(*args, **kwargs)

	@property
	def poll_set(self):
		return self.polls.filter(approved = True).order_by('pk').all()

	def display_content(self):
		content = smart_unicode(self.content)
		content = content.replace('<<ANOTACIA>>', '<div class="annotation">' + self.annotation + '</div>')
		content = content.replace('{SHAKAL_PREFIX}', '/')
		return mark_safe(content)

	def clean_fields(self, exclude = None):
		slug_num = None
		try:
			slug_num = int(self.slug)
		except ValueError:
			pass
		if slug_num is not None:
			raise ValidationError({'slug': [_('Numeric slug values are not allowed')]})
		super(Article, self).clean_fields(exclude)

	@permalink
	def get_absolute_url(self):
		return ('article:detail', None, {'slug': self.slug})

	@permalink
	def get_list_url(self):
		return ('article:list', None, None)

	def is_published(self):
		return self.published and self.pub_time <= now()

	def __unicode__(self):
		return self.title

	class Meta:
		verbose_name = _('article')
		verbose_name_plural = _('articles')
