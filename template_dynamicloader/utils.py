# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.conf import settings


def switch_template(request, **kwargs):
	template = kwargs['template']
	css = kwargs['css']
	template_settings = kwargs['settings']
	try:
		if template.split(',', 1)[0] in settings.DYNAMIC_TEMPLATES:
			request.session['template_skin'] = template
			request.session['template_css'] = css
			request.session['template_settings'] = template_settings
		else:
			return
	except KeyError:
		return


def decode_switch_template(data):
	if data:
		try:
			template, data = data.split(':', 1)
		except ValueError:
			template = data
			data = ''
	else:
		template = 'default'
	extra_css = None
	template_settings = {}
	if data:
		extra_css, data = data.split(':', 1)
		if data:
			try:
				template_settings = json.loads(data)
			except ValueError:
				pass
	return (template, extra_css, template_settings)


def get_template_settings(request):
	template_skin = css = template_settings = None

	templates = settings.DYNAMIC_TEMPLATES
	default = settings.DYNAMIC_TEMPLATES[0]

	if request is None:
		return (default, css, {})

	if request.method == 'GET' and 'switch_template' in request.GET:
		template_skin, css, template_settings = decode_switch_template(request.GET['switch_template'])
	else:
		template_settings = request.session.get('template_settings', '')
		if template_settings:
			try:
				template_settings = json.loads(template_settings)
			except ValueError:
				pass
		else:
			template_settings = {}

	if template_skin is None:
		template_skin = request.session.get('template_skin', default)
	if not template_skin.split(',', 1)[0] in templates:
		template_skin = default


	return (template_skin, css, template_settings)
