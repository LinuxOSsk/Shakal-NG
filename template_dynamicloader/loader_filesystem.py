# -*- coding: utf-8 -*-

from django.conf import settings
from django.template import TemplateDoesNotExist, loader
from django.template.loader import BaseLoader
from template_dynamicloader.settings import TEMPLATE_DEFAULT_SKIN, TEMPLATE_DEFAULT_DEVICE
from template_dynamicloader.middleware import get_request
import os

class Loader(BaseLoader):
	is_usable = True

	""" Iterátor pre prechádzanie ostatných loaderov """
	@property
	def other_loaders(self):
		for template_loader in loader.template_source_loaders:
			if template_loader != self:
				yield template_loader

	""" Vráti adresár s templatmi pre zariadenie, ktoré používa návštevnik. """
	def get_specific_template_dir(self):
		request = get_request()
		# Nastavenie aktuálneho zariadenia a skinu
		try:
			template_device = request.session['template_device']
		except KeyError:
			template_device = TEMPLATE_DEFAULT_DEVICE;
		try:
			template_skin = request.session['template_skin']
		except KeyError:
			template_skin = TEMPLATE_DEFAULT_SKIN;
		return os.path.join(template_device, template_skin)

	""" Vráti šablónu špecifickú pre zariadenie. """
	def get_specific_template(self, template_name):
		return os.path.join(self.get_specific_template_dir(), template_name)

	def load_template(self, template_name, template_dirs = None):
		specific_template = self.get_specific_template(template_name)
		for template_loader in self.other_loaders:
			try:
				return template_loader.load_template(specific_template, template_dirs)
			except TemplateDoesNotExist:
				pass
		raise TemplateDoesNotExist(specific_template)

	def load_template_source(self, template_name, template_dirs = None):
		specific_template = self.get_specific_template(template_name)
		for template_loader in self.other_loaders:
			try:
				return template_loader.load_template_source(specific_template, template_dirs)
			except TemplateDoesNotExist:
				pass
			# Daný loader podporuje len load_template
			except NotImplementedError:
				pass
		raise TemplateDoesNotExist(specific_template)


