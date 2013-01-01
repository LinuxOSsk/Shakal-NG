# -*- coding: utf-8 -*-

import mptt
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime


class Page(models.Model):
	TYPE_CHOICES = (
		('h', u'Domovská stránka'),
		('i', u'Interná stránka'),
		('p', u'Stránka wiki'),
	)
	title = models.CharField(max_length = 100, verbose_name = u'titulok')
	created = models.DateTimeField(editable = False)
	updated = models.DateTimeField(editable = False)
	last_author = models.ForeignKey(User, verbose_name = u'posledný autor')
	slug = models.SlugField(unique = True, verbose_name = u'slug')
	parent = models.ForeignKey('self', related_name = 'children', blank = True, null = True, verbose_name = u'nadradená stránka')
	text = models.TextField(verbose_name = u'text')
	page_type = models.CharField(max_length = 1, choices = TYPE_CHOICES, default = 'p', verbose_name = u'typ stránky')

	def save(self, *args, **kwargs):
		self.updated = datetime.now()
		if not self.id:
			self.created = self.updated
		super(Page, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.title

	class Meta:
		verbose_name = u'Wiki stránka'
		verbose_name_plural = u'Wiki stránky'

	@models.permalink
	def get_absolute_url(self):
		if self.page_type == 'h' and not self.parent:
			return ('wiki:home', None, None)
		else:
			return ('wiki:page', None, {'slug': self.slug})

mptt.register(Page)
