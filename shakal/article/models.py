# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class Category(models.Model):
	name = models.CharField(max_length = 255, verbose_name = _('name'))
	slug = models.CharField(max_length = 255)
	icon = models.CharField(max_length = 255, verbose_name = _('icon'))

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = _('category')
		verbose_name_plural = _('categories')


class Article(models.Model):
	title = models.CharField(max_length = 255, verbose_name = _('title'))
	slug = models.CharField(max_length = 255)
	category = models.ForeignKey(Category, on_delete = models.PROTECT, verbose_name = _('category'))
	perex = models.TextField(verbose_name = _('perex'), help_text = _('Text on title page.'))
	annotation = models.TextField(verbose_name = _('annotation'), help_text = _('Text before article body.'))
	content = models.TextField(verbose_name = _('content'))
	author = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True, verbose_name = _('author'))
	authors_name = models.CharField(max_length = 255, verbose_name = _('authors name'))
	time = models.DateTimeField()
	published = models.BooleanField(verbose_name = _('published'))
	top = models.BooleanField(verbose_name = _('top article'))
	image = models.ImageField(verbose_name = _('image'), upload_to = '/article/thumbnails', blank = True, null = True)
	display_count = models.IntegerField(verbose_name = _('display count'), default = 0)

	def __unicode__(self):
		return self.title

	class Meta:
		verbose_name = _('article')
		verbose_name_plural = _('articles')
