# -*- coding: utf-8 -*-
from json import dumps

from django.conf import settings
from django.forms import Textarea
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from .parser import ALL_TAGS
from .syntax import LEXERS


class TextVal(str):
	@property
	def field_format(self):
		return self.split(':', 1)[0] if ':' in self else ''

	@property
	def field_text(self):
		return self.split(':', 1)[1] if ':' in self else ''


class RichEditorMixin(Textarea):
	class Media:
		js = [
			'js/richeditor/editor2.js',
		]
		css = {
			'screen': [
				'css/editor.light.css',
			],
		}

	def __init__(self, attrs=None, **kwargs):
		self.language = settings.LANGUAGE_CODE
		self.formats = ()
		self.skin = 'shakal'
		super(RichEditorMixin, self).__init__(attrs)

	def get_tags_info(self, supported_tags):
		unsupported_tags = set(ALL_TAGS) - set(supported_tags) - set(('html', 'body'))
		return {
			'unsupported': list(unsupported_tags),
			'known': list(supported_tags),
		}


class RichEditor(RichEditorMixin):
	def render(self, name, value, attrs=None, **kwargs):
		supported_tags = self.attrs.pop('supported_tags', {})
		self.attrs.pop('parsers_conf', {})
		widget = super(RichEditor, self).render(name, value, attrs)

		context = {
			'name': name,
			'lang': self.language[:2],
			'tags': dumps(self.get_tags_info(supported_tags)),
			'widget': widget,
			'lexers': dumps(LEXERS),
		}
		return mark_safe(render_to_string('widgets/editor.html', context))


class RichOriginalEditor(RichEditorMixin):
	def __init__(self, formats=(('html', 'HTML'), ), *args, **kwargs):
		super(RichOriginalEditor, self).__init__(*args, **kwargs)
		self.formats = formats

	def get_template_name(self):
		return 'widgets/editor.html'

	def render(self, name, value, attrs=None, **kwargs):
		if value is None:
			field_format = self.formats[0][0]
			text = ''
		else:
			field_format = value.field_format
			text = value.field_text

		formats = []
		for fmt, label in self.formats:
			formats.append({
				'format': fmt,
				'label': label,
				'checked': fmt == field_format
			})
		if not field_format in dict(self.formats):
			formats[0]['checked'] = True

		supported_tags = self.attrs.pop('supported_tags', {})
		parsers_conf = self.attrs.pop('parsers_conf', {})
		widget = super(RichOriginalEditor, self).render(name, text, attrs)

		context = {
			'name': name,
			'lang': self.language[:2],
			'tags': dumps(self.get_tags_info(supported_tags)),
			'parsers': dumps(parsers_conf),
			'widget': widget,
			'format': field_format,
			'formats': formats,
			'skin': self.skin,
			'lexers': dumps(LEXERS),
		}
		return mark_safe(render_to_string(self.get_template_name(), context))

	def value_from_datadict(self, data, files, name):
		text = data.get(name)
		if self.attrs.get('no_format'):
			return text
		fmt = data.get(name + "_format") or self.formats[0][0]
		if not fmt in dict(self.formats):
			fmt = self.formats[0][0]
		return TextVal(fmt + ':' + text)
