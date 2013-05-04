# -*- coding: utf-8 -*-
from django.forms import CharField

from rich_editor.parser import HtmlParser
from .widgets import RichOriginalEditor, RichEditor


class RichTextField(CharField):
	widget = RichEditor

	def __init__(self, *args, **kwargs):
		self.parser = HtmlParser()
		super(RichTextField, self).__init__(*args, **kwargs)

	def widget_attrs(self, widget):
		attrs = super(RichTextField, self).widget_attrs(widget)
		attrs.update(self.parser.get_attributes())
		return attrs


class RichOriginalField(CharField):
	widget = RichOriginalEditor

	def __init__(self, parser = HtmlParser, *args, **kwargs):
		self.parser = parser()
		super(RichOriginalField, self).__init__(*args, **kwargs)

	def widget_attrs(self, widget):
		attrs = super(RichOriginalField, self).widget_attrs(widget)
		attrs.update(self.parser.get_attributes())
		return attrs

	def clean(self, value):
		return (value[0], super(RichOriginalField, self).clean(value[1]))
