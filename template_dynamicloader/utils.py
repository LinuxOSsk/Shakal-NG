# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings


def switch_template(request, template, css):
	try:
		if template.split(',', 1)[0] in settings.DYNAMIC_TEMPLATES:
			request.session['template_skin'] = template
			request.session['template_css'] = css
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
	if data:
		extra_css = data
	return (template, extra_css)


def get_template_settings(request):
	template_skin = css = None
	if request.method == 'GET' and 'switch_template' in request.GET:
		template_skin, css = decode_switch_template(request.GET['switch_template'])

	templates = settings.DYNAMIC_TEMPLATES
	default = settings.DYNAMIC_TEMPLATES[0]

	if template_skin is None:
		template_skin = request.session.get('template_skin', default)
	if not template_skin.split(',', 1)[0] in templates:
		template_skin = default

	return (template_skin, css)
