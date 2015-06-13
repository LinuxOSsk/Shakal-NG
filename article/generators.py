# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_autoslugfield.utils import unique_slugify
from django_sample_generator import GeneratorRegister, ModelGenerator, samples

from .models import Category


class CategoryGenerator(ModelGenerator):
	name = samples.NameSample()
	description = samples.ParagraphSample()

	def get_object(self):
		obj = super(CategoryGenerator, self).get_object()
		unique_slugify(obj, 'slug')
		return obj


register = GeneratorRegister()
register.register(CategoryGenerator(Category, 4))
