# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.conf import settings

from common_utils.cookies import set_cookie


def switch_template(response, **kwargs):
	template = kwargs['template']
	css = kwargs['css']
	template_settings = kwargs['settings']
	try:
		if template.split(',', 1)[0] in settings.DYNAMIC_TEMPLATES:
			cookie_val = json.dumps({
				'skin': template,
				'css': css,
				'settings': template_settings,
			})
			set_cookie(response, 'user_template', cookie_val)
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
		try:
			extra_css, data = data.split(':', 1)
			if data:
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
		user_template = request.COOKIES.get('user_template', '')
		if user_template:
			try:
				user_template = json.loads(user_template)
				user_template['settings'] = json.loads(user_template['settings'])
				template_skin = user_template.get('skin', None)
				css = user_template.get('css', '')
				template_settings = user_template.get('settings', {})
			except ValueError:
				pass

	if template_skin is None:
		template_skin = request.session.get('template_skin', default)
	if not template_skin in templates:
		template_skin = default

	return (template_skin, css, template_settings)
