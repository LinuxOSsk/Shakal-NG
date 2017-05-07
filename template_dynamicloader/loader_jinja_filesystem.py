# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import FileSystemLoader, BaseLoader
from itertools import chain
import os

from .loader_filesystem import DynamicLoaderMixin
from django.conf import settings


class JinjaLoader(DynamicLoaderMixin, FileSystemLoader):
	def __init__(self, engine):
		from django.template.loaders import app_directories
		dirs = tuple(engine.dirs) + app_directories.get_app_template_dirs('templates')
		self.forward_loaders = {}
		self.default_loader = None
		for name in settings.DYNAMIC_TEMPLATES:
			dynamic_dirs = ((os.path.join(dirname, 'template_overrides', name), dirname) for dirname in dirs)
			dynamic_dirs = list(chain(*dynamic_dirs))
			loader = FileSystemLoader(dynamic_dirs)
			if self.default_loader is None:
				self.default_loader = loader
			self.forward_loaders[name] = loader
		print(self.forward_loaders)

	def get_source(self, environment, template):
		loader = self.forward_loaders.get(self.get_dynamic_template(), self.default_loader)
		print(loader)
		return loader.get_source(environment, template)

	#is_usable = True
	#_accepts_engine_in_init = True

	#def __init__(self, engine):
	#	from django.template.loaders import app_directories
	#	super(JinjaLoader, self).__init__(tuple(engine.dirs) + app_directories.get_app_template_dirs('templates'))
	#	from django.conf import settings
	#	auto_reload = {t['BACKEND']: t for t in settings.TEMPLATES}['template_dynamicloader.backend.Jinja2']["OPTIONS"].get('auto_reload', False)
	#	cache_enable = not auto_reload
	#	self.template_source_cache = {} if cache_enable else None

	#def get_template_source(self, template, environment):
	#	if self.template_source_cache is None:
	#		return super(JinjaLoader, self).get_source(environment, template)
	#	else:
	#		if not template in self.template_source_cache:
	#			try:
	#				self.template_source_cache[template] = super(JinjaLoader, self).get_source(environment, template)
	#			except:
	#				self.template_source_cache[template] = None
	#				raise
	#		template_source = self.template_source_cache[template]
	#		if template_source is None:
	#			raise TemplateNotFound(template)
	#		return template_source

	#def get_source(self, environment, template):
	#	visitors_template = self.get_visitors_template(template)
	#	try:
	#		return self.get_template_source(visitors_template, environment)
	#	except TemplateNotFound:
	#		return self.get_template_source(template, environment)

	#def load(self, environment, name, globals=None):
	#	print(name)
	#	return super(JinjaLoader, self).load(environment, name, globals)
