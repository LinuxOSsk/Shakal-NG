# -*- coding: utf-8 -*-
from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import FileSystemLoader
from .loader_filesystem import DynamicLoaderMixin
from django.conf import settings
from django.template.loaders import app_directories


class JinjaLoader(DynamicLoaderMixin, FileSystemLoader):
	def __init__(self):
		super(JinjaLoader, self).__init__(tuple(settings.TEMPLATE_DIRS) + app_directories.app_template_dirs)
		self.template_source_cache = {}

	def get_source(self, environment, template):
		visitors_template = self.get_visitors_template(template)
		if visitors_template in self.template_source_cache:
			if self.template_source_cache[visitors_template] is None:
				raise TemplateNotFound(visitors_template)
			else:
				return self.template_source_cache[visitors_template]
		try:
			source = super(JinjaLoader, self).get_source(environment, self.get_visitors_template(template))
		except TemplateNotFound:
			try:
				source = super(JinjaLoader, self).get_source(environment, template)
			except TemplateNotFound:
				self.template_source_cache[visitors_template] = None
				raise
		self.template_source_cache[visitors_template] = source
		return source
