# -*- coding: utf-8 -*-
from django.conf import settings
from django_autoslugfield.utils import unique_slugify
from django_sample_generator import fields, generator
from accounts.models import User

from .models import Blog, Post
from common_utils import generator_fields as extra_generator_fields


class BlogGenerator(generator.ModelGenerator):
	author_id = fields.ForeignKeyFieldGenerator(
		queryset=User.objects.all().order_by('pk').values_list('pk', flat=True),
		random_data=False
	)
	title = extra_generator_fields.SentenceFieldGenerator(max_length=20)
	original_description = extra_generator_fields.LongHtmlFieldGenerator(paragraph_count=1)
	original_sidebar = extra_generator_fields.LongHtmlFieldGenerator(paragraph_count=1)

	def get_object(self):
		obj = super(BlogGenerator, self).get_object()
		obj.filtered_description = obj.original_description
		obj.filtered_sidebar = obj.original_sidebar
		unique_slugify(obj, 'slug')
		return obj

	class Meta:
		model = Blog
		fields = ('created', 'updated')
		unique_checks = (('title',),)


class PostGenerator(generator.ModelGenerator):
	title = extra_generator_fields.SentenceFieldGenerator(max_length=50)
	original_perex = extra_generator_fields.LongHtmlFieldGenerator(paragraph_count=1)
	original_content = extra_generator_fields.LongHtmlFieldGenerator()

	def get_object(self):
		obj = super(PostGenerator, self).get_object()
		obj.filtered_perex = obj.original_perex
		obj.filtered_content = obj.original_content
		unique_slugify(obj, 'slug')
		return obj

	class Meta:
		model = Post
		fields = ('blog', 'pub_time', 'created', 'updated', 'linux')
		unique_checks = (('title',),)


generators = [
	BlogGenerator(settings.INITIAL_DATA_COUNT['accounts_user']),
	PostGenerator(settings.INITIAL_DATA_COUNT['blog_post']),
]
