# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_autoslugfield.utils import unique_slugify
from django_sample_generator import GeneratorRegister, ModelGenerator, samples

from .models import News
from accounts.models import User
from django.conf import settings


class NewsGenerator(ModelGenerator):
	title = samples.SentenceSample(unique=True)
	original_short_text = samples.ParagraphSample()
	author_id = samples.RelationSample(queryset=User.objects.all().order_by("pk"), random_data=True, only_pk=True, fetch_all=True)
	authors_name = samples.NameSample()
	created = samples.DateTimeSample()
	updated = samples.DateTimeSample()

	def get_object(self):
		obj = super(NewsGenerator, self).get_object()
		obj.title = obj.title[:50]
		obj.filtered_short_text = obj.original_short_text[1]
		obj.original_long_text = obj.original_short_text[1]
		obj.filtered_long_text = obj.original_long_text[1]
		obj.approved = True
		unique_slugify(obj, 'slug')
		return obj


register = GeneratorRegister()
register.register(NewsGenerator(News, settings.INITIAL_DATA_COUNT['news_news']))
