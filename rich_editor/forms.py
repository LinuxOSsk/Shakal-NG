# -*- coding: utf-8 -*-
from django.forms import CharField

from rich_editor.parser import HtmlParser, RawParser
from .widgets import RichOriginalEditor, RichEditor, AdminRichOriginalEditor


class RichTextField(CharField):
	widget = RichEditor

	def __init__(self, *args, **kwargs):
		self.parser = kwargs.pop('parser', HtmlParser())
		super(RichTextField, self).__init__(*args, **kwargs)

	def widget_attrs(self, widget):
		attrs = super(RichTextField, self).widget_attrs(widget)
		attrs.update(self.parser.get_attributes())
		return attrs

	def clean(self, value):
		self.parser.parse(value)
		return self.parser.get_output()


class RichOriginalField(CharField):
	widget = RichOriginalEditor

	def __init__(self, parsers, *args, **kwargs):
		self.parsers = parsers
		super(RichOriginalField, self).__init__(*args, **kwargs)

	def widget_attrs(self, widget):
		attrs = super(RichOriginalField, self).widget_attrs(widget)
		attrs.update(self.parsers['html'].get_attributes())
		return attrs

	def clean(self, value):
		fmt = value[0]
		txt = super(RichOriginalField, self).clean(value[1])
		parser = self.parsers[fmt]
		parser.parse(txt)
		parsed = parser.get_output()
		return (fmt, txt, parsed)


class AdminRichOriginalField(RichOriginalField):
	widget = AdminRichOriginalEditor

	def __init__(self, parsers, *args, **kwargs):
		parsers['raw'] = RawParser()
		super(AdminRichOriginalField, self).__init__(parsers, *args, **kwargs)
