# -*- coding: utf-8 -*-

from django.forms import CharField
from html_editor.parser import HtmlParser
from widgets import HtmlEditor

class HtmlField(CharField):
	widget = HtmlEditor

	def __init__(self, *args, **kwargs):
		self.parser = HtmlParser()
		super(HtmlField, self).__init__(*args, **kwargs)

	def widget_attrs(self, widget):
		attrs = super(HtmlField, self).widget_attrs(widget)
		attrs['supported_tags'] = self.parser.supported_tags
		return attrs

	def to_python(self, value):
		self.parser.parse(value)
		return self.parser.get_output()
