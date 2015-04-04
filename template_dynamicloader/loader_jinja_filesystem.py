# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import FileSystemLoader

from .loader_filesystem import DynamicLoaderMixin


class JinjaLoader(DynamicLoaderMixin, FileSystemLoader):
	def __init__(self, *args, **kwargs):
		super(JinjaLoader, self).__init__(*args, **kwargs)
		from django.conf import settings
		cache_enable = getattr(settings, 'JINJA2_BYTECODE_CACHE_ENABLE', False)
		self.template_source_cache = {} if cache_enable else None

	def get_template_source(self, template, environment):
		if self.template_source_cache is None:
			return super(JinjaLoader, self).get_source(environment, template)
		else:
			if not template in self.template_source_cache:
				self.template_source_cache[template] = None
				self.template_source_cache[template] = super(JinjaLoader, self).get_source(environment, template)
			template_source = self.template_source_cache[template]
			if template_source is None:
				raise TemplateNotFound(template)
			return template_source

	def get_source(self, environment, template):
		visitors_template = self.get_visitors_template(template)
		try:
			return self.get_template_source(visitors_template, environment)
		except TemplateNotFound:
			return self.get_template_source(template, environment)
