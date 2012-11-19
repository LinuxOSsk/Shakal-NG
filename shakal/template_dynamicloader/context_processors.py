# -*- coding: utf-8 -*-

from shakal.template_dynamicloader.utils import get_template_settings


class StyleOptions:
	def __init__(self, options_data):
		if not options_data:
			pass
		print(options_data)
		for option in options_data.split(','):
			try:
				(name, value) = option.split('=', 1)
				setattr(self, name, value)
			except ValueError:
				setattr(self, option, True)


def style(request):
	(template_device, template_skin, template_css) = get_template_settings(request)
	try:
		options = template_skin.split(',', 1)[1]
	except IndexError:
		options = ''
	return {'style_options': StyleOptions(options), 'style_css': template_css}
