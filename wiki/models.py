# -*- coding: utf-8 -*-
import mptt
from django_autoslugfield.fields import AutoSlugField
from django.conf import settings
from django.db import models
from django.utils import timezone

from rich_editor.fields import RichTextOriginalField, RichTextFilteredField


class Page(mptt.models.MPTTModel):
	TYPE_CHOICES = (
		('h', u'Domovská stránka'),
		('i', u'Interná stránka'),
		('p', u'Stránka wiki'),
	)
	title = models.CharField(u'titulok', max_length = 255)
	created = models.DateTimeField(editable = False)
	updated = models.DateTimeField(editable = False)
	last_author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name = u'posledný autor', blank = True, null = True)
	slug = AutoSlugField(unique = True, verbose_name = u'slug', title_field = 'title')
	parent = models.ForeignKey('self', related_name = 'children', blank = True, null = True, verbose_name = u'nadradená stránka')
	original_text = RichTextOriginalField(filtered_field = "filtered_text", property_name = "text")
	filtered_text = RichTextFilteredField()
	page_type = models.CharField(u'typ stránky', max_length = 1, choices = TYPE_CHOICES, default = 'p')

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
