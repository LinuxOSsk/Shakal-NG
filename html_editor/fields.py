# -*- coding: utf-8 -*-

from django.forms import CharField
from html_editor.parser import HtmlParser
from widgets import HtmlEditor

class HtmlField(CharField):
	widget = HtmlEditor

	def to_python(self, value):
		parser = HtmlParser()
		parser.parse(value)
		return parser.get_output()
