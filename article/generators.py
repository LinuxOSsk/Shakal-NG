# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django_autoslugfield.utils import unique_slugify
from django_sample_generator import generator, fields

from .models import Category, Article
from common_utils import generator_fields as extra_generator_fields
from hitcount.models import HitCount


class CategoryGenerator(generator.ModelGenerator):
	name = extra_generator_fields.NameFieldGenerator(uppercase_word=True)

	def get_object(self):
		obj = super(CategoryGenerator, self).get_object()
		unique_slugify(obj, 'slug')
		return obj

	class Meta:
		model = Category
		fields = ('description',)
		unique_checks = [('name',),]


class ArticleGenerator(generator.ModelGenerator):
	title = extra_generator_fields.SentenceFieldGenerator()
	authors_name = extra_generator_fields.NameFieldGenerator()
	original_perex = extra_generator_fields.LongHtmlFieldGenerator(paragraph_count=1)
	original_content = extra_generator_fields.LongHtmlFieldGenerator()

	def get_object(self):
		obj = super(ArticleGenerator, self).get_object()
		obj.title = obj.title[:50]
		obj.original_annotation = obj.original_perex
		obj.filtered_annotation = obj.original_annotation
		obj.filtered_perex = obj.original_perex
		obj.filtered_content = obj.original_content
		obj.published = True
		obj.created = obj.updated
		unique_slugify(obj, 'slug')
		return obj

	class Meta:
		model = Article
		unique_checks = [('title',),]
		fields = ('category', 'pub_time', 'updated', 'author', 'top')


class HitCountGenerator(generator.ModelGenerator):
	object_id = fields.ForeignKeyFieldGenerator(
		queryset=Article.all_articles.all().order_by('pk').values_list('pk', flat=True),
		random_data=False
	)

	class Meta:
		model = HitCount
		fields = ('hits',)

	def __init__(self, *args, **kwargs):
		super(HitCountGenerator, self).__init__(*args, **kwargs)
		self.content_type = ContentType.objects.get_for_model(Article)

	def get_object(self):
		obj = super(HitCountGenerator, self).get_object()
		obj.content_type = self.content_type
		return obj


generators = [
	CategoryGenerator(settings.INITIAL_DATA_COUNT['article_category']),
	ArticleGenerator(settings.INITIAL_DATA_COUNT['article_article']),
	HitCountGenerator(settings.INITIAL_DATA_COUNT['article_article']),
]
