# -*- coding: utf-8 -*-
from django.conf import settings
from django_autoslugfield.utils import unique_slugify
from django_sample_generator import fields, generator

from .models import Tweet
from accounts.models import User
from common_utils import generator_fields as extra_generator_fields


class TweetGenerator(generator.ModelGenerator):
	title = extra_generator_fields.SentenceFieldGenerator(max_length=50)
	original_text = extra_generator_fields.LongHtmlFieldGenerator(paragraph_count=1)
	author_id = fields.ForeignKeyFieldGenerator(
		queryset=User.objects.all().order_by('pk').values_list('pk', flat=True),
		random_data=False
	)

	class Meta:
		model = Tweet
		fields = ('created', 'updated')
		unique_checks = (('title',),)

	def get_object(self):
		obj = super(TweetGenerator, self).get_object()
		obj.filtered_text = obj.original_text
		unique_slugify(obj, 'slug')
		return obj


generators = [
	TweetGenerator(settings.INITIAL_DATA_COUNT['tweets_tweet'])
]
