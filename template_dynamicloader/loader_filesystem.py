# -*- coding: utf-8 -*-

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import BaseLoader
from template_dynamicloader.settings import TEMPLATE_DEFAULT_NAME, TEMPLATE_DEFAULT_DEVICE
from template_dynamicloader.middleware import get_request
import os

class Loader(BaseLoader):
	is_usable = True
	def get_template_sources(self, template_file, template_dirs = None):
		if not template_dirs:
			template_dirs = settings.TEMPLATE_DIRS

		# vyhľdanie užívateľom nastavených šablón
		request = get_request()
		defaultTemplate = True
		try:
			template_device = request.session['template_device']
			defaultTemplate = False
		except KeyError:
			template_device = TEMPLATE_DEFAULT_DEVICE;

		try:
			template_name = request.session['template_name']
			defaultTemplate = False
		except KeyError:
			template_device = TEMPLATE_DEFAULT_NAME;
		print(request.session.keys())

		if not defaultTemplate:
			for template_dir in template_dirs:
				yield os.path.join(template_dir, template_device, template_name, template_file)
		for template_dir in template_dirs:
			yield os.path.join(template_dir, TEMPLATE_DEFAULT_DEVICE, TEMPLATE_DEFAULT_NAME, template_file)

	def load_template_source(self, template_name, template_dirs = None):
		tried = []
		for filePath in self.get_template_sources(template_name, template_dirs):
			try:
				tplFile = open(filePath)
				try:
					return (tplFile.read().decode(settings.FILE_CHARSET), filePath)
				finally:
					tplFile.close()
			except IOError:
				tried.append(filePath)
		raise TemplateDoesNotExist("Tried: {0}".format(tried))

