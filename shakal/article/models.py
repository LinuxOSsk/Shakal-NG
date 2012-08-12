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
	def get_query_set(self):
		table = Article._meta.db_table
		join_tables = []
		model_definition = [Article]
		query = 'SELECT '
		columns = []
		for field in Article._meta.fields:
			if field.name == 'content':
				continue
			elif isinstance(field, models.ForeignKey):
				model = field.related.parent_model
				col_names = [f.name for f in model._meta.fields]
				columns += ['"'+model._meta.db_table+'"."'+c+'"' for c in col_names]
				model_definition.append([model, field.name] + col_names)
				join_type = 'LEFT OUTER' if field.null else 'INNER'
				join_tables.append(' '+join_type+' JOIN "'+model._meta.db_table+'" ON ("'+table+'"."'+field.column+'" = "'+model._meta.db_table+'"."id")')
			else:
				columns.append('"' + table + '"."' + field.column + '"')
				model_definition.append(field.column)

		columns += ['"'+RootHeader._meta.db_table+'"."comment_count"', '"'+RootHeader._meta.db_table+'"."last_comment"']
		model_definition += ['comment_count', 'last_comment']
		columns += ['"'+HitCount._meta.db_table+'"."hits"']
		model_definition += ['display_count']

		query += ', '.join(columns)
		query += ' FROM "' + table + '"'
		query += ''.join(join_tables)
		query += ' LEFT OUTER JOIN "' + RootHeader._meta.db_table + '"';
		query += ' ON ("'+table+'"."id" = "'+RootHeader._meta.db_table+'"."object_id" AND "'+RootHeader._meta.db_table+'"."content_type_id" = '+str(ContentType.objects.get_for_model(Article).id)+')'
		query += ' LEFT OUTER JOIN "' + HitCount._meta.db_table + '"';
		query += ' ON ("'+table+'"."id" = "'+HitCount._meta.db_table+'"."object_id" AND "'+HitCount._meta.db_table+'"."content_type_id" = '+str(ContentType.objects.get_for_model(Article).id)+')'
		query += ' WHERE "'+table+'"."time" < %s AND "'+table+'"."published" = %s'
		query += ' ORDER BY "'+table+'"."id" DESC'

		params = [datetime.now(), True]
		queryset = super(ArticleListManager, self).get_query_set(query, model_definition = model_definition, params = params)
		return queryset


class ArticleAbstract(models.Model):
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
		abstract = True


class Article(ArticleAbstract):
	class Meta:
		verbose_name = _('article')
		verbose_name_plural = _('articles')


class ArticleView(ArticleAbstract):
	class Meta:
		managed = False


def create_article_hitcount(sender, **kwargs):
	article = kwargs['instance']
	if not article.hitcount.all():
		hc = HitCount(content_object = article)
		hc.save()

post_save.connect(create_article_hitcount, sender = Article)
