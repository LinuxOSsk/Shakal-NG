# -*- coding: utf-8 -*-
from django.forms import CharField

from .parser import HtmlParser
from .syntax import highlight_pre_blocks
from .widgets import RichOriginalEditor, RichEditor, TextVal


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

	def __init__(self, parsers, parsers_conf, supported_tags, *args, **kwargs):
		self.parsers = parsers
		self.parsers_conf = parsers_conf
		self.supported_tags = supported_tags
		super(RichOriginalField, self).__init__(*args, **kwargs)

	def widget_attrs(self, widget):
		attrs = super(RichOriginalField, self).widget_attrs(widget)
		attrs['parsers_conf'] = self.parsers_conf
		attrs['supported_tags'] = self.supported_tags
		for parser in self.parsers.values():
			attrs.update(parser.get_attributes())
		return attrs

	def clean(self, value):
		fmt = value.field_format
		txt = super(RichOriginalField, self).clean(value.field_text)
		if fmt in self.parsers:
			parser = self.parsers.get(fmt, self.parsers[fmt])
			parser.parse(txt)
			parsed = parser.get_output()
		else:
			parsed = txt
		parsed = highlight_pre_blocks(parsed)
		val = TextVal(fmt + ':' + txt)
		val.field_filtered = parsed
		return val
