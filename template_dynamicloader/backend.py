# -*- coding: utf-8 -*-
from django.template.engine import Engine
from django_jinja import backend


class Jinja2(backend.Jinja2):
	pass
	#def __init__(self, params):
	#	options = params.pop('ENGINE_OPTIONS')
	#	dirs = list(params.get('DIRS'))
	#	app_dirs = bool(params.get('APP_DIRS'))
	#	self.engine = Engine(dirs, app_dirs, **options)
	#	params['OPTIONS']['loader'] = self.engine.template_loaders[0]
	#	super(Jinja2, self).__init__(params)
