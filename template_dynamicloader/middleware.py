# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

import json
from django.template.loader import render_to_string
from django.utils.encoding import force_text

from .forms import ChangeTemplateHiddenForm
from .utils import decode_switch_template


class TemplateSwitcherMiddleware(object):
	def wrap_content(self, request, content, template_data):
		match = re.search('<body[^>]*>', content)
		if match is None:
			raise ValueError
		template, extra_css, template_settings = template_data
		form = ChangeTemplateHiddenForm({
			'template': template,
			'css': extra_css,
			'settings': json.dumps(template_settings)
		})
		confirm = render_to_string('template_dynamicloader/switch_confirm_inline.html', {'form': form}, request=request)
		return force_text(content[0:match.end(0)]) + confirm + force_text(content[match.end(0):])

	def process_response(self, request, response):
		if response.status_code != 200:
			return response
		if request.method == 'GET' and 'switch_template' in request.GET:
			template = decode_switch_template(request.GET['switch_template'])
			response.content = self.wrap_content(request, response.content, template)
		return response
