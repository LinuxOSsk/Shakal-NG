# -*- coding: utf-8 -*-

from django.conf import settings


def switch_template(request, device, template, css):
	try:
		device_templates = dict(settings.TEMPLATES)[device]
		if template is None:
			template = device_templates[0]
		else:
			if template in device_templates:
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
