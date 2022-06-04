# -*- coding: utf-8 -*-
import json
from collections import namedtuple

from django.conf import settings as django_settings

from common_utils.cookies import set_cookie


UserTemplateSettings = namedtuple('UserTemplateSettings', ('template', 'css', 'settings'))


def get_default_template(request):
	request_time = getattr(request, 'request_time', None)
	if request_time is None:
		return (django_settings.DYNAMIC_TEMPLATES[0], None, {})
	t = request_time.date()
	if t.day == 1 and t.month == 4:
		return ('386', None, {})
	else:
		return (django_settings.DYNAMIC_TEMPLATES[0], None, {})



def switch_template(response, template, css, settings, **kwargs):
	try:
		if template in django_settings.DYNAMIC_TEMPLATES:
			cookie_val = json.dumps({
				'skin': template,
				'css': css,
				'settings': settings,
			})
			set_cookie(response, 'user_template', cookie_val, cookie_age=3600 * 24 * 365 * 10)
		else:
			return
	except KeyError:
		return


def decode_switch_template(data):
	data = data.split(':', 2)
	if len(data) == 3:
		try:
			data[2] = json.loads(data[2])
		except ValueError:
			data[2] = {}
	else:
		defaults = ['', '', {}]
		data += defaults[len(data):]
	return UserTemplateSettings(*data)


def get_template_settings(request):
	if hasattr(request, '_template_settings'):
		return getattr(request, '_template_settings')

	template_skin = css = template_settings = None

	templates = django_settings.DYNAMIC_TEMPLATES
	default = get_default_template(request)

	if request is None:
		return UserTemplateSettings(*default)

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
		template_skin, css, template_settings = default

	result = UserTemplateSettings(template_skin, css, template_settings)
	setattr(request, '_template_settings', result)
	return result
