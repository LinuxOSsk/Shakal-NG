# -*- coding: utf-8 -*-

import mptt
from django.db import models


class Page(models.Model):
	TYPE_CHOICES = (
		('h', u'Domovská stránka'),
		('i', u'Interná stránka'),
		('l', u'Stránka so zoznamom podstránok'),
		('p', u'Stránka wiki'),
	)
	title = models.CharField(max_length = 100, verbose_name = u'titulok')
	created = models.DateTimeField(auto_now_add = True)
	modified = models.DateTimeField(auto_now = True)
	slug = models.SlugField(unique = True, verbose_name = u'slug')
	parent = models.ForeignKey('self', related_name = 'children', blank = True, null = True, verbose_name = u'nadradená stránka')
	text = models.TextField(verbose_name = u'text')
	page_type = models.CharField(max_length = 1, choices = TYPE_CHOICES, default = 'p', verbose_name = u'typ stránky')

	def __unicode__(self):
		return self.title

	class Meta:
		verbose_name = u'Wiki stránka'
		verbose_name_plural = u'Wiki stránky'

	@models.permalink
	def get_absolute_url(self):
		return ('wiki:page', None, {'slug': self.slug})

mptt.register(Page)
