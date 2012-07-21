# -*- coding: utf-8 -*-

from django.template import TemplateDoesNotExist, loader
from django.template.loader import BaseLoader
from shakal.template_dynamicloader.settings import TEMPLATE_DEFAULT_SKIN, TEMPLATE_DEFAULT_DEVICE
from django_tools.middlewares.ThreadLocal import get_current_request
import os

class Loader(BaseLoader):
	is_usable = True

	@property
	def other_template_loaders(self):
		for template_loader in loader.template_source_loaders:
			if template_loader != self:
				yield template_loader

	def get_visitors_template_dir(self):
		request = get_current_request()

		try:
			template_device = request.session['template_device']
		except KeyError:
			template_device = TEMPLATE_DEFAULT_DEVICE

		try:
			template_skin = request.session['template_skin']
		except KeyError:
			template_skin = TEMPLATE_DEFAULT_SKIN;

		return os.path.join(template_device, template_skin)

	def get_visitors_template(self, template_name):
		return os.path.join(self.get_visitors_template_dir(), template_name)

	def load_template(self, template_name, template_dirs = None):
		return self.direct_load_template(template_name, template_dirs, 'load_template')

	def load_template_source(self, template_name, template_dirs = None):
		return self.direct_load_template(template_name, template_dirs, 'load_template_source')

	def direct_load_template(self, template_name, template_dirs, load_type):
		visitors_template = self.get_visitors_template(template_name)
		for template_loader in self.other_template_loaders:
			try:
				return getattr(template_loader, load_type)(visitors_template, template_dirs)
			except TemplateDoesNotExist:
				pass
			except NotImplementedError:
				pass
			except AttributeError:
				pass
		raise TemplateDoesNotExist(visitors_template)

