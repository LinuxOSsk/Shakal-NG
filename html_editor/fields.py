# -*- coding: utf-8 -*-

from django.forms import CharField
from html_editor.parser import HtmlParser

class HtmlField(CharField):
	def to_python(self, value):
		parser = HtmlParser()
		parser.parse(value)
		return parser.get_output()
