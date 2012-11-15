# -*- coding: utf-8 -*-

import re
from django.template.loader import render_to_string
from django.utils.encoding import smart_unicode

class TemplateSwitcherMiddleware(object):
	def decode_switch_template(self, data):
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

	def wrap_content(self, content):
		match = re.search('<body[^>]*>', content)
		if match is None:
			raise ValueError
		confirm = render_to_string('template_dynamicloader/switch_confirm_inline.html', {})
		return smart_unicode(content[0:match.end(0)]) + confirm + smart_unicode(content[match.end(0):])

	def process_response(self, request, response):
		if response.status_code != 200:
			return response
		if request.method == 'GET' and 'switch_template' in request.GET:
			device, template, extra_css = self.decode_switch_template(request.GET['switch_template'])
			response.content = self.wrap_content(response.content)
		return response
