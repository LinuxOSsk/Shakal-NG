# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from autoimagefield.fields import AutoImageField
from datetime import datetime
from hitcount.models import HitCount

class Category(models.Model):
	name = models.CharField(max_length = 255, verbose_name = _('name'))
	slug = models.SlugField()
	icon = models.CharField(max_length = 255, verbose_name = _('icon'))

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = _('category')
		verbose_name_plural = _('categories')


class ArticleListManager(models.Manager):
	def get_query_set(self):
		return super(ArticleListManager, self).get_query_set().select_related('author', 'category').filter(time__lte = datetime.now(), published = True).order_by('-pk').annotate(display_count = models.Sum('hitcount__hits'))


class Article(models.Model):
	objects = models.Manager()
	articles = ArticleListManager()

	title = models.CharField(max_length = 255, verbose_name = _('title'))
	slug = models.SlugField(unique = True)
	category = models.ForeignKey(Category, on_delete = models.PROTECT, verbose_name = _('category'))
	perex = models.TextField(verbose_name = _('perex'), help_text = _('Text on title page.'))
	annotation = models.TextField(verbose_name = _('annotation'), help_text = _('Text before article body.'))
	content = models.TextField(verbose_name = _('content'))
	author = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True, verbose_name = _('author'))
	authors_name = models.CharField(max_length = 255, verbose_name = _('authors name'))
	time = models.DateTimeField(verbose_name = _('publication time'))
	published = models.BooleanField(verbose_name = _('published'))
	top = models.BooleanField(verbose_name = _('top article'))
	image = AutoImageField(verbose_name = _('image'), upload_to = 'article/thumbnails', size = (512, 512), thumbnail = {'standard': (100, 100)}, blank = True, null = True)
	hitcount = generic.GenericRelation(HitCount)

	def clean(self):
		slug_num = None
		try:
			slug_num = int(self.slug)
		except:
			pass
		if slug_num is not None:
			raise ValidationError(_('Numeric slug values are not allowed'))

	def __unicode__(self):
		return self.title

	class Meta:
		verbose_name = _('article')
		verbose_name_plural = _('articles')


def create_article_hitcount(sender, **kwargs):
	article = kwargs['instance']
	if not article.hitcount.all():
		hc = HitCount(content_object = article)
		hc.save()

post_save.connect(create_article_hitcount, sender = Article)
