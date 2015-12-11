# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from braces.views import CsrfExemptMixin
from django.views.generic import View
from django.http.response import HttpResponse

from rich_editor import get_parser
from rich_editor.syntax import highlight_pre_blocks


class Preview(CsrfExemptMixin, View):
	def post(self, request, **kwargs):
		fmt = request.POST.get('format', 'html')
		parser = request.POST.get('parser', '')
		text = request.POST.get('text')[:500000] # ochrana
		parser_instance = get_parser(parser, fmt)
		parser_instance.parse(text)
		parsed = parser_instance.get_output()
		return HttpResponse(highlight_pre_blocks(parsed))
