# -*- coding: utf-8 -*-
from django.forms import CharField

from rich_editor.parser import HtmlParser
from widgets import RichEditor


class RichTextField(CharField):
	widget = RichEditor

	def __init__(self, parser = HtmlParser, *args, **kwargs):
		self.parser = parser()
		super(RichTextField, self).__init__(*args, **kwargs)

	def widget_attrs(self, widget):
		attrs = super(RichTextField, self).widget_attrs(widget)
		attrs.update(self.parser.get_attributes())
		return attrs

	def to_python(self, value):
		self.parser.parse(value)
		return self.parser.get_output()
