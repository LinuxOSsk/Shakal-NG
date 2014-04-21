# -*- coding: utf-8 -*-
from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import FileSystemLoader
from .loader_filesystem import DynamicLoaderMixin
from django.conf import settings
from django.template.loaders import app_directories


class JinjaLoader(DynamicLoaderMixin, FileSystemLoader):
	def __init__(self):
		super(JinjaLoader, self).__init__(app_directories.app_template_dirs + tuple(settings.TEMPLATE_DIRS))

	def get_source(self, environment, template):
		try:
			return super(JinjaLoader, self).get_source(environment, self.get_visitors_template(template))
		except TemplateNotFound:
			return super(JinjaLoader, self).get_source(environment, template)
