# -*- coding: utf-8 -*-
from django.conf import settings
from django.forms import Textarea
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from json import dumps

from rich_editor.parser import ALL_TAGS


class RichEditorMixin(Textarea):
	class Media:
		js = [
			'js/richeditor/editor.js',
		]
		css = {
			'screen': ['css/editor.light.css'],
		}

	def __init__(self, attrs=None, **kwargs):
		self.language = settings.LANGUAGE_CODE
		self.formats = ()
		self.skin = 'shakal'
		super(RichEditorMixin, self).__init__(attrs)

	def get_tags_info(self, supported_tags):
		unsupported_tags = set(ALL_TAGS) - set(supported_tags.keys()) - set(('html', 'body'))
		defined_tags = set(supported_tags.keys()) - set('')
		for tag in supported_tags:
			if tag == '':
				tag_name = 'body'
			else:
				tag_name = tag
			unsupported_tags.update([tag_name + ' > ' + t for t in defined_tags - supported_tags[tag].get_child_tags() if t != ''])
		return {
			'unsupported': list(unsupported_tags),
			'known': supported_tags.keys(),
		}


class RichEditor(RichEditorMixin):
	def render(self, name, value, attrs=None, **kwargs):
		supported_tags = self.attrs.pop('supported_tags', {})
		parsers_conf = self.attrs.pop('parsers_conf', {})
		widget = super(RichEditor, self).render(name, value, attrs)

		context = {
			'name': name,
			'lang': self.language[:2],
			'tags': dumps(self.get_tags_info(supported_tags)),
			'parsers': dumps(parsers_conf),
			'widget': widget,
		}
		return mark_safe(render_to_string('widgets/editor.html', context))


class RichOriginalEditor(RichEditorMixin):
	template_name = 'widgets/editor.html'

	def __init__(self, formats=(('html', 'HTML'), ), *args, **kwargs):
		super(RichOriginalEditor, self).__init__(*args, **kwargs)
		self.formats = formats

	def render(self, name, value, attrs=None, **kwargs):
		if value is None:
			value=(None, None)
		try:
			value_fmt, value = value
		except ValueError:
			value_fmt = self.formats[0][0]

		formats = []
		for fmt, label in self.formats:
			formats.append({'format': fmt, 'label': label, 'checked': fmt == value_fmt})
		if not value_fmt in dict(self.formats):
			formats[0]['checked'] = True

		supported_tags = self.attrs.pop('supported_tags', {})
		parsers_conf = self.attrs.pop('parsers_conf', {})
		widget = super(RichOriginalEditor, self).render(name, value, attrs)

		context = {
			'name': name,
			'lang': self.language[:2],
			'tags': dumps(self.get_tags_info(supported_tags)),
			'parsers': dumps(parsers_conf),
			'widget': widget,
			'format': value_fmt,
			'formats': formats,
			'skin': self.skin
		}
		return mark_safe(render_to_string(self.template_name, context))

	def value_from_datadict(self, data, files, name):
		text = data.get(name)
		if isinstance(text, tuple):
			return text
		if not text:
			return ('html', text)
		fmt = data.get(name + "_format")
		if self.attrs.get('no_format'):
			return text
		else:
			return (fmt, text)
