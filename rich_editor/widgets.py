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
			'js/lib.js',
			'js/richeditor/editor.js',
		]
		css = {
			'screen': ['css/editor.css'],
		}

	def __init__(self, attrs=None, **kwargs):
		self.language = settings.LANGUAGE_CODE
		self.formats = ()
		self.skin = 'shakal'
		attrs = attrs or {}
		attrs.update({'class': 'input-xlarge'})
		super(RichEditorMixin, self).__init__(attrs)

	def get_tags_info(self):
		supported_tags = self.attrs.get('supported_tags', {})
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
		widget = super(RichEditor, self).render(name, value, attrs)
		self.attrs['supported_tags'] = supported_tags

		context = {
			'name': name,
			'lang': self.language[:2],
			'tags': dumps(self.get_tags_info()),
			'widget': widget,
		}
		return mark_safe(render_to_string('widgets/editor.html', context))


class RichOriginalEditor(RichEditorMixin):
	def __init__(self, formats=(('html', 'HTML'), ), *args, **kwargs):
		super(RichOriginalEditor, self).__init__(*args, **kwargs)
		self.formats = formats

	def render(self, name, value, attrs=None, **kwargs):
		if value is None:
			value=(None, None)
		value_fmt, value = value

		formats = []
		for fmt, label in self.formats:
			formats.append({'format': fmt, 'label': label, 'checked': fmt == value_fmt})
		if not value_fmt in dict(self.formats):
			formats[0]['checked'] = True

		supported_tags = self.attrs.pop('supported_tags', {})
		widget = super(RichOriginalEditor, self).render(name, value, attrs)
		self.attrs['supported_tags'] = supported_tags

		context = {
			'name': name,
			'lang': self.language[:2],
			'tags': dumps(self.get_tags_info()),
			'widget': widget,
			'format': value_fmt,
			'formats': formats,
			'skin': self.skin
		}
		return mark_safe(render_to_string('widgets/editor.html', context))

	def value_from_datadict(self, data, files, name):
		text = data.get(name)
		if isinstance(text, tuple):
			return text
		if not text:
			return ('html', text)
		fmt = data.get(name + "_format")
		return (fmt, text)


class AdminRichOriginalEditor(RichOriginalEditor):
	class Media:
		js = [
			'js/lib.js',
			'js/richeditor/editor.js',
		]
		css = {
		}

	def __init__(self, *args, **kwargs):
		super(AdminRichOriginalEditor, self).__init__(*args, **kwargs)
		self.formats = self.formats + (('raw', 'RAW'), )
		self.skin = 'compact'
