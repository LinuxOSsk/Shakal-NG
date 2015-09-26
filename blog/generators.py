# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django_autoslugfield.utils import unique_slugify
from django_sample_generator import GeneratorRegister, ModelGenerator, samples

from .models import Blog, Post
from accounts.models import User
from common_utils.samples import LongHtmlGenerator


class BlogGenerator(ModelGenerator):
	author_id = samples.RelationSample(queryset=User.objects.all().order_by("pk"), random_data=False, only_pk=True, fetch_all=True)
	title = samples.SentenceSample(unique=True, max_length=20)
	original_description = samples.ParagraphSample()
	original_sidebar = samples.ParagraphSample()
	created = samples.DateTimeSample()
	updated = samples.DateTimeSample()

	def get_object(self):
		obj = super(BlogGenerator, self).get_object()
		obj.filtered_description = obj.original_description[1]
		obj.filtered_sidebar = obj.original_sidebar[1]
		unique_slugify(obj, 'slug')
		return obj


class PostGenerator(ModelGenerator):
	blog_id = samples.RelationSample(queryset=Blog.objects.all().order_by("pk"), random_data=True, only_pk=True, fetch_all=True)
	title = samples.SentenceSample(unique=True, max_length=50)
	original_perex = samples.ParagraphSample(max_length=500)
	original_content = LongHtmlGenerator()
	pub_time = samples.DateTimeSample()
	created = samples.DateTimeSample()
	updated = samples.DateTimeSample()
	linux = samples.BooleanSample()

	def get_object(self):
		obj = super(PostGenerator, self).get_object()
		obj.filtered_perex = obj.original_perex[1]
		obj.filtered_content = obj.original_content[1]
		unique_slugify(obj, 'slug')
		return obj

register = GeneratorRegister()
register.register(BlogGenerator(Blog, settings.INITIAL_DATA_COUNT['accounts_user']))
register.register(PostGenerator(Post, settings.INITIAL_DATA_COUNT['blog_post']))
