# -*- coding: utf-8 -*-
from django.conf import settings
from django_sample_generator import fields, generator

from .models import Section, Topic
from accounts.models import User
from common_utils import generator_fields as extra_generator_fields


class TopicGenerator(generator.ModelGenerator):
	section_id = fields.ForeignKeyFieldGenerator(
		queryset=Section.objects.all().order_by("pk").values_list('pk', flat=True),
		random_data=True,
	)
	title = extra_generator_fields.SentenceFieldGenerator(max_length=60)
	original_text = extra_generator_fields.LongHtmlFieldGenerator(paragraph_count=1)

	author_id = fields.ForeignKeyFieldGenerator(
		queryset=User.objects.all().order_by('pk').values_list('pk', flat=True),
		random_data=True
	)
	authors_name = extra_generator_fields.NameFieldGenerator()

	class Meta:
		model = Topic
		fields = ('created', 'updated')
		unique_checks = (('title',),)

	def get_object(self):
		obj = super(TopicGenerator, self).get_object()
		obj.filtered_text = obj.original_text
		obj.updated = obj.created
		return obj


generators = [
	TopicGenerator(settings.INITIAL_DATA_COUNT['forum_topic'])
]
