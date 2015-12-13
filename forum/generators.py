# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.conf import settings
from django_sample_generator import GeneratorRegister, ModelGenerator, samples

from .models import Section, Topic
from accounts.models import User


class TopicGenerator(ModelGenerator):
	section_id = samples.RelationSample(queryset=Section.objects.all().order_by("pk"), random_data=True, only_pk=True, fetch_all=True)
	title = samples.SentenceSample()
	original_text = samples.ParagraphSample()
	created = samples.DateTimeSample(min_date=datetime.now() - timedelta(14), max_date=datetime.now())
	author_id = samples.RelationSample(queryset=User.objects.all().order_by("pk"), random_data=True, only_pk=True, fetch_all=True)
	authors_name = samples.NameSample()

	def get_object(self):
		obj = super(TopicGenerator, self).get_object()
		obj.filtered_text = obj.original_text.field_text
		obj.updated = obj.created
		obj.title = obj.title[:60]
		return obj


register = GeneratorRegister()
register.register(TopicGenerator(Topic, settings.INITIAL_DATA_COUNT['forum_topic']))
