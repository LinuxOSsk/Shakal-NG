# -*- coding: utf-8 -*-
import mptt
from django.conf import settings
from django.db import models
from django.utils import timezone


class Page(models.Model):
	TYPE_CHOICES = (
		('h', u'Domovská stránka'),
		('i', u'Interná stránka'),
		('p', u'Stránka wiki'),
	)
	title = models.CharField(max_length = 255, verbose_name = u'titulok')
	created = models.DateTimeField(editable = False)
	updated = models.DateTimeField(editable = False)
	last_author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name = u'posledný autor', blank = True, null = True)
	slug = models.SlugField(unique = True, verbose_name = u'slug')
	parent = models.ForeignKey('self', related_name = 'children', blank = True, null = True, verbose_name = u'nadradená stránka')
	text = models.TextField(verbose_name = u'text')
	page_type = models.CharField(max_length = 1, choices = TYPE_CHOICES, default = 'p', verbose_name = u'typ stránky')

	def save(self, *args, **kwargs):
		if not kwargs.pop('ignore_auto_date', False):
			self.updated = timezone.now()
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
