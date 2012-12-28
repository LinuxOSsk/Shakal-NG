# -*- coding: utf-8 -*-

from django.contrib.contenttypes import generic
from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from shakal.threaded_comments.models import RootHeader


class NewsManager(models.Manager):
	def get_query_set(self):
		return super(NewsManager, self).get_query_set().select_related('author')


class NewsListManager(models.Manager):
	def get_query_set(self):
		return super(NewsListManager, self).get_query_set().select_related('author').filter(approved = True).order_by('-pk')


class News(models.Model):
	objects = NewsManager()
	news = NewsListManager()

	title = models.CharField(max_length = 255, verbose_name = _('title'))
	slug = models.SlugField(unique = True)
	short_text = models.TextField(verbose_name = _('short text'))
	long_text = models.TextField(verbose_name = _('long text'))
	time = models.DateTimeField(default = datetime.now, verbose_name = _('time'))
	author = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True, verbose_name = _('user'))
	authors_name = models.CharField(max_length = 255, verbose_name = _('authors name'))
	approved = models.BooleanField(default = False, verbose_name = _('approved'))
	comments_header = generic.GenericRelation(RootHeader)

	class Meta:
		verbose_name = _('news item')
		verbose_name_plural = _('news items')

	@permalink
	def get_absolute_url(self):
		return ('news:detail-by-slug', None, {'slug': self.slug})

	@permalink
	def get_list_url(self):
		return ('news:list', None, None)

	def __unicode__(self):
		return self.title
