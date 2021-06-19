# -*- coding: utf-8 -*-
import json
import re

from django.template.loader import render_to_string
from django.utils.encoding import force_bytes

from .forms import ChangeTemplateHiddenForm
from .utils import decode_switch_template


class TemplateSwitchMiddleware(object):
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		response = self.get_response(request)
		if response.status_code != 200:
			return response
		if request.method == 'GET' and 'switch_template' in request.GET:
			template = decode_switch_template(request.GET['switch_template'])
			response.content = self.wrap_content(request, response.content, template)
		return response

	def wrap_content(self, request, content, template_data):
		match = re.search(force_bytes('<body[^>]*>'), content)
		if match is None:
			raise ValueError
		template, extra_css, template_settings = template_data
		form = ChangeTemplateHiddenForm({
			'template': template,
			'css': extra_css,
			'settings': json.dumps(template_settings),
			'next': request.path
		})
		confirm = force_bytes(render_to_string('template_dynamicloader/switch_confirm_inline.html', {'form': form}, request=request))
		return force_bytes(content[0:match.end(0)]) + confirm + force_bytes(content[match.end(0):])
