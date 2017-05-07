# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template.engine import Engine
from django_jinja import backend
from .loader_filesystem import DynamicLoaderMixin
import jinja2


class Jinja2(DynamicLoaderMixin, backend.Jinja2):
	def __init__(self, params):
		options = params.pop('ENGINE_OPTIONS')
		dirs = list(params.get('DIRS'))
		app_dirs = bool(params.get('APP_DIRS'))
		self.engine = Engine(dirs, app_dirs, **options)
		params['OPTIONS']['loader'] = self.engine.template_loaders[0]
		super(Jinja2, self).__init__(params)

	def get_template(self, template_name):
		try:
			return super(Jinja2, self).get_template(self.get_visitors_template(template_name))
		except:
			return super(Jinja2, self).get_template(template_name)
