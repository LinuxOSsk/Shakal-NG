# -*- coding: utf-8 -*-

from django import template

def process_template_params(rawparams, context = None):
	params = {}
	for param in rawparams:
		paramname = param
		paramvalue = ''
		try:
			pos = param.index('=')
			paramname = param[:pos]
			paramvalue = param[pos + 1:]
			if context is not None:
				paramvalue = template.resolve_variable(paramvalue, context)
		except KeyError:
			paramvalue = True
			pass
		params[paramname] = paramvalue
	return params
