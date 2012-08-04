# -*- coding: utf-8 -*-

from django.db import connection, models
from django.db.models import permalink
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from generic_aggregation import generic_annotate


class NewsManager(models.Manager):
	def get_query_set(self):
		return super(NewsManager, self).get_query_set().select_related('author')


class NewsListManager(models.Manager):
	def get_query_set(self):
		if connection.vendor == 'postgresql':
			queryset = QuerySet(NewsView, using = self._db)
			queryset = queryset.extra(select = {'last_comment': 'last_comment', 'comment_count': 'comment_count'})
		else:
			queryset = QuerySet(News, using = self._db)
			queryset = generic_annotate(queryset, RootHeader, models.Max('comments_header__last_comment'), alias = 'last_comment')
			queryset = generic_annotate(queryset, RootHeader, models.Max('comments_header__comment_count'), alias = 'comment_count')
		queryset = queryset.select_related('author')
		return queryset


class NewsAbstract(models.Model):
	objects = NewsManager()
	news = NewsListManager()

	subject = models.CharField(max_length = 255, verbose_name = _('subject'))
	slug = models.SlugField(unique = True)
	short_text = models.TextField(verbose_name = _('short text'))
	long_text = models.TextField(verbose_name = _('long text'))
	time = models.DateTimeField(default = datetime.now, verbose_name = _('time'))
	author = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True, verbose_name = _('user'))
	authors_name = models.CharField(max_length = 255, verbose_name = _('authors name'))
	approved = models.BooleanField(default = False, verbose_name = _('approved'))

	class Meta:
		abstract = True

	@permalink
	def get_absolute_url(self):
		return ('news:detail-by-slug', None, {'slug': self.slug})

	def __unicode__(self):
		return self.subject


class News(NewsAbstract):
	class Meta:
		verbose_name = _('news item')
		verbose_name_plural = _('news items')


class NewsView(NewsAbstract):
	class Meta:
		managed = False
