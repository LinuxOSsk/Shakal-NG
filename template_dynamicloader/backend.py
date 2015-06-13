# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_jinja.backend import Jinja2 as CoreJinja2

from .loader_jinja_filesystem import JinjaLoader


class Jinja2(CoreJinja2):
	def __init__(self, params):
		from django.template.loaders import app_directories

		options = params['OPTIONS']
		options['loader'] = JinjaLoader(tuple(params['DIRS']) + app_directories.get_app_template_dirs('templates'))
		super(Jinja2, self).__init__(params)
