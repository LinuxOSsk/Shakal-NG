# -*- coding: utf-8 -*-

from django import template


def process_template_args(rawparams, context = None):
	args = []
	for param in rawparams:
		pos = param.find('=')
		if (pos > 0):
			break
		if context is not None:
			param = template.resolve_variable(param, context)
		args.append(param)
	return args


def process_template_kwargs(rawparams, context = None):
	kwargs = {}
	for param in rawparams:
		paramname = param
		paramvalue = ''
		pos = param.find('=')
		if (pos <= 0):
			continue
		paramname = param[:pos]
		paramvalue = param[pos + 1:]
		if context is not None:
			paramvalue = template.resolve_variable(paramvalue, context)
		kwargs[paramname] = paramvalue
	return kwargs
