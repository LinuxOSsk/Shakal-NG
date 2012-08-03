# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import connection, models
from django.db.models.signals import post_save
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from autoimagefield.fields import AutoImageField
from datetime import datetime
from generic_aggregation import generic_annotate
from hitcount.models import HitCount
from shakal.survey.models import Survey
from shakal.threaded_comments.models import RootHeader

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


class ArticleListManager(models.Manager):
	def get_query_set(self):
		queryset = super(ArticleListManager, self).get_query_set()
		queryset = queryset.select_related()
		queryset = queryset.select_related('author', 'category')
		queryset = queryset.filter(time__lte = datetime.now(), published = True)
		queryset = queryset.order_by('-pk')
		return queryset


class ArticleListAggregateManager(ArticleListManager):
	def get_query_set(self):
		queryset = super(ArticleListAggregateManager, self).get_query_set()
		queryset = generic_annotate(queryset, HitCount.objects.all(), models.Max('hitcount__hits'), alias = 'display_count')
		queryset = generic_annotate(queryset, RootHeader, models.Max('comments_header__last_comment'), alias = 'last_comment')
		queryset = generic_annotate(queryset, RootHeader, models.Max('comments_header__comment_count'), alias = 'comment_count')
		return queryset


class ArticleAbstract(models.Model):
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
	hitcount = generic.GenericRelation(HitCount, content_type_field = 'content_type_id', object_id_field = 'object_id')
	surveys = generic.GenericRelation(Survey)
	comments_header = generic.GenericRelation(RootHeader)
	@property
	def survey_set(self):
		return self.surveys.filter(approved = True).order_by('pk').all()

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

	def __unicode__(self):
		return self.title

	class Meta:
		abstract = True


class Article(ArticleAbstract):
	objects = models.Manager()
	articles = ArticleListAggregateManager()

	class Meta:
		verbose_name = _('article')
		verbose_name_plural = _('articles')


class ArticleView(ArticleAbstract):
	objects = models.Manager()
	articles = ArticleListManager()

	display_count = models.PositiveIntegerField()
	comment_count = models.PositiveIntegerField()
	last_comment = models.DateTimeField()

	class Meta:
		managed = False


def create_article_hitcount(sender, **kwargs):
	article = kwargs['instance']
	if not article.hitcount.all():
		hc = HitCount(content_object = article)
		hc.save()

post_save.connect(create_article_hitcount, sender = Article)


def article_model():
	if connection.vendor == 'postgresql':
		return ArticleView
	else:
		return Article
