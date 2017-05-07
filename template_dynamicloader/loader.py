# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.template import TemplateDoesNotExist
from django.template.loaders.base import Loader as BaseLoader

from template_dynamicloader.utils import get_template_settings
from web.middlewares.threadlocal import get_current_request


class Loader(BaseLoader):
	@property
	def other_template_loaders(self):
		next_loaders = False
		for template_loader in self.engine.template_loaders:
			if next_loaders:
				yield template_loader
			if template_loader == self:
				next_loaders = True

	def get_visitors_template_dir(self):
		request = get_current_request()
		template_skin = get_template_settings(request)[0]
		return os.path.join('overrides', template_skin.split(',')[0])

	def get_visitors_template(self, template_name):
		return os.path.join(self.get_visitors_template_dir(), template_name)

	def get_template_sources(self, template_name, *args, **kwargs):
		sources = []
		visitors_template = self.get_visitors_template(template_name)
		for template_loader in self.other_template_loaders:
			sources += template_loader.get_template_sources(visitors_template, *args, **kwargs)
		for template_loader in self.other_template_loaders:
			sources += template_loader.get_template_sources(template_name, *args, **kwargs)
		return sources

	def get_contents(self, origin):
		return origin.loader.get_contents(origin)

	def load_template_source(self, template_name, *args, **kwargs):
		visitors_template = self.get_visitors_template(template_name)
		try:
			return self.direct_load_template(visitors_template, *args, **kwargs)
		except TemplateDoesNotExist:
			return self.direct_load_template(template_name, *args, **kwargs)

	def direct_load_template(self, template_name, *args, **kwargs):
		for template_loader in self.other_template_loaders:
			try:
				return template_loader.load_template_source(template_name, *args, **kwargs)
			except TemplateDoesNotExist:
				pass
			except NotImplementedError:
				pass
			except AttributeError:
				pass
		raise TemplateDoesNotExist(template_name)
