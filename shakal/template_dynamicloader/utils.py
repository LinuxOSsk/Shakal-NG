# -*- coding: utf-8 -*-

from django.conf import settings
from shakal.template_dynamicloader.settings import TEMPLATE_DEFAULT_SKIN, TEMPLATE_DEFAULT_DEVICE


def switch_template(request, device, template, css):
	try:
		device_templates = dict(settings.TEMPLATES)[device]
		if template is None:
			template = device_templates[0]
		else:
			if template.split(',', 1)[0] in device_templates:
				request.session['template_device'] = device
				request.session['template_skin'] = template
				request.session['template_css'] = css
			else:
				return
	except KeyError:
		return


def decode_switch_template(data):
	device, data = data.split(':', 1)
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
	return (device, template, extra_css)


def get_template_settings(request):
	try:
		template_device = request.session['template_device']
		templates = dict(settings.TEMPLATES)
		if not template_device in templates:
			template_device = TEMPLATE_DEFAULT_DEVICE
	except KeyError:
		template_device = TEMPLATE_DEFAULT_DEVICE

	device_templates = set({})
	if template_device in templates:
		device_templates = templates[template_device]

	try:
		template_skin = request.session['template_skin']
		if not template_skin in device_templates:
			template_skin = TEMPLATE_DEFAULT_SKIN
	except KeyError:
		template_skin = TEMPLATE_DEFAULT_SKIN

	css = None
	if request.method == 'GET' and 'switch_template' in request.GET:
		(template_device, template_skin, css) = decode_switch_template(request.GET['switch_template'])

	return (template_device, template_skin, css)
