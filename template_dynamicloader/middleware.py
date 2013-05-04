# -*- coding: utf-8 -*-
import re

from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.encoding import smart_unicode

from template_dynamicloader.forms import ChangeTemplateHiddenForm
from template_dynamicloader.utils import decode_switch_template


class TemplateSwitcherMiddleware(object):
	def wrap_content(self, request, content, template_data):
		match = re.search('<body[^>]*>', content)
		if match is None:
			raise ValueError
		device, template, extra_css = template_data
		form = ChangeTemplateHiddenForm({'device': device, 'template': template, 'css': extra_css})
		confirm = render_to_string('template_dynamicloader/switch_confirm_inline.html', RequestContext(request, {'form': form}))
		return smart_unicode(content[0:match.end(0)]) + confirm + smart_unicode(content[match.end(0):])

	def process_response(self, request, response):
		if response.status_code != 200:
			return response
		if request.method == 'GET' and 'switch_template' in request.GET:
			template = decode_switch_template(request.GET['switch_template'])
			response.content = self.wrap_content(request, response.content, template)
		return response
