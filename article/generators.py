# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template.defaultfilters import slugify
from django_sample_generator import GeneratorRegister, ModelGenerator, samples

from .models import Category


class CategoryGenerator(ModelGenerator):
	name = samples.NameSample()
	description = samples.ParagraphSample()

	def get_object(self):
		obj = super(CategoryGenerator, self).get_object()
		obj.slug = slugify(obj.name)
		return obj


register = GeneratorRegister()
register.register(CategoryGenerator(Category, 4))
