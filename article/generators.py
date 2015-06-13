# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_autoslugfield.utils import unique_slugify
from django_sample_generator import GeneratorRegister, ModelGenerator, samples
from accounts.models import User

from .models import Category, Article


class CategoryGenerator(ModelGenerator):
	name = samples.NameSample()
	description = samples.ParagraphSample()

	def get_object(self):
		obj = super(CategoryGenerator, self).get_object()
		unique_slugify(obj, 'slug')
		return obj


class ArticleGenerator(ModelGenerator):
	title = samples.SentenceSample()
	category_id = samples.RelationSample(queryset=Category.objects.all().order_by("pk"), random_data=True, only_pk=True, fetch_all=True)
	perex = samples.ParagraphSample()
	content = samples.LongTextSample()
	author_id = samples.RelationSample(queryset=User.objects.all().order_by("pk"), random_data=True, only_pk=True, fetch_all=True)
	authors_name = samples.NameSample()
	pub_time = samples.DateTimeSample()
	updated = samples.DateTimeSample()
	top = samples.BooleanSample()

	def get_object(self):
		obj = super(ArticleGenerator, self).get_object()
		obj.title = obj.title[:50]
		obj.annotation = obj.perex
		obj.published = True
		unique_slugify(obj, 'slug')
		return obj


register = GeneratorRegister()
register.register(CategoryGenerator(Category, 4))
register.register(ArticleGenerator(Article, 10))
