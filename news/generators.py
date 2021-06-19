# -*- coding: utf-8 -*-
from django.conf import settings
from django_autoslugfield.utils import unique_slugify
from django_sample_generator import fields, generator

from .models import News, Category
from accounts.models import User
from common_utils import generator_fields as extra_generator_fields


class NewsGenerator(generator.ModelGenerator):
	title = extra_generator_fields.SentenceFieldGenerator(max_length=50)
	category_id = fields.ForeignKeyFieldGenerator(
		queryset=Category.objects.all().order_by("pk").values_list('pk', flat=True),
		random_data=True
	)
	original_short_text = extra_generator_fields.LongHtmlFieldGenerator(paragraph_count=1)
	author_id = fields.ForeignKeyFieldGenerator(
		queryset=User.objects.all().order_by('pk').values_list('pk', flat=True),
		random_data=False
	)
	authors_name = extra_generator_fields.NameFieldGenerator()

	class Meta:
		model = News
		fields = ('created', 'updated')
		unique_checks = (('title',),)

	def get_object(self):
		obj = super(NewsGenerator, self).get_object()
		obj.filtered_short_text = obj.original_short_text
		obj.original_long_text = obj.original_short_text
		obj.filtered_long_text = obj.original_long_text
		obj.approved = True
		unique_slugify(obj, 'slug')
		return obj


generators = [
	NewsGenerator(settings.INITIAL_DATA_COUNT['news_news'])
]
