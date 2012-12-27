# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.db.models import permalink
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from autoimagefield.fields import AutoImageField
from datetime import datetime
from hitcount.models import HitCount
from shakal.survey.models import Survey
from shakal.threaded_comments.models import CommentCountManager, RootHeader

class Category(models.Model):
	name = models.CharField(max_length = 255, verbose_name = _('name'))
	slug = models.SlugField(unique = True)
	icon = models.CharField(max_length = 255, verbose_name = _('icon'))

	@permalink
	def get_absolute_url(self):
		return ('article:list-category', None, {'category': self.slug})

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name = _('category')
		verbose_name_plural = _('categories')


class ArticleListManager(CommentCountManager):
	def _generate_query_set(self, extra_filter = '', extra_params = []):
		table = Article._meta.db_table
		model_definition, query = self._generate_query(Article, ['"'+HitCount._meta.db_table+'"."hits"'], ['display_count'], skip = set(('content', )))
		query += ' LEFT OUTER JOIN "' + HitCount._meta.db_table + '"';
		query += ' ON ("'+table+'"."id" = "'+HitCount._meta.db_table+'"."object_id" AND "'+HitCount._meta.db_table+'"."content_type_id" = '+str(ContentType.objects.get_for_model(Article).id)+')'
		query += ' WHERE "'+table+'"."time" < %s AND "'+table+'"."published" = %s'
		query += extra_filter
		query += ' ORDER BY "'+table+'"."id" DESC'

		params = [datetime.now(), True] + extra_params
		return super(ArticleListManager, self).get_raw_query_set(query, model_definition = model_definition, params = params)

	def filter(self, category = None, top = None):
		table = Article._meta.db_table
		where = '';
		params = []
		if category is not None:
			where += ' AND "'+table+'"."category_id" = %s'
			params.append(category.pk)
		if top is not None:
			where += ' AND "'+table+'"."top" = %s'
			params.append(top)
		return self._generate_query_set(where, params)

	def exclude(self, pk):
		table = Article._meta.db_table
		return self._generate_query_set(' AND "'+table+'"."id" != %s', [pk])

	def get_query_set(self):
		return self._generate_query_set()


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
	surveys = generic.GenericRelation(Survey)
	comments_header = generic.GenericRelation(RootHeader)

	@property
	def survey_set(self):
		return self.surveys.filter(approved = True).order_by('pk').all()

	def display_content(self):
		content = self.content
		content = content.replace('<<ANOTACIA>>', '<div class="annotation">' + self.annotation + '</div>')
		return mark_safe(content)

	def hit(self):
		article_type = ContentType.objects.get_for_model(self.__class__)
		hit_count = HitCount.objects.get_or_create(content_type = article_type, object_id = self.pk)[0]
		hit_count.hits += 1
		hit_count.save()
	hit.alters_data = True

	def clean(self):
		slug_num = None
		try:
			slug_num = int(self.slug)
		except:
			pass
		if slug_num is not None:
			raise ValidationError(_('Numeric slug values are not allowed'))

	@permalink
	def get_absolute_url(self):
		return ('article:detail-by-slug', None, {'slug': self.slug})

	@permalink
	def get_list_url(self):
		return ('article:article-list', None, None)

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
