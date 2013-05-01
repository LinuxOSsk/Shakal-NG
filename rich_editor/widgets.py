# -*- coding: utf-8 -*-
from django.conf import settings
from django.forms import Textarea
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from json import dumps

from rich_editor.parser import ALL_TAGS


class RichEditor(Textarea):
	class Media:
		js = [
			'js/richeditor/editor.js',
		]
		css = {
			'all': ('js/wymeditor/skins/shakal/skin.css', )
		}

	def __init__(self, attrs = {}, **kwargs):
		self.language = settings.LANGUAGE_CODE
		self.formats = (('html', 'HTML'), )
		attrs.update({'class': 'wymeditor'})
		super(RichEditor, self).__init__(attrs)

	def render(self, name, value, attrs = None, **kwargs):
		supported_tags = self.attrs.pop('supported_tags', {})
		format_inputs = []
		if value is None:
			value_fmt = None
			value = None
		else:
			value_fmt, value = value
		for fmt, label in self.formats:
			checked = ' checked="checked"' if fmt == value_fmt else ''
			input_text = '<input type="radio" name="' + mark_safe(name + '_format') + '" value="' + mark_safe(fmt) + '" ' + checked + '/> '
			format_inputs.append('<label>' + input_text + mark_safe(label) + '</label>')
		widget = mark_safe(u'<div class="textareawrapper">' + ''.join(format_inputs)) + super(RichEditor, self).render(name, value, attrs) + mark_safe(u'</div>')
		self.attrs['supported_tags'] = supported_tags
		unsupported_tags = set(ALL_TAGS) - set(supported_tags.keys()) - set(('html', 'body'))
		defined_tags = set(supported_tags.keys()) - set('')
		for tag in supported_tags:
			if tag == '':
				tag_name = 'body'
			else:
				tag_name = tag
			unsupported_tags.update([tag_name + ' > ' + t for t in defined_tags - supported_tags[tag].get_child_tags() if t != ''])
		tags_info = {
			'unsupported': list(unsupported_tags),
			'known': supported_tags.keys(),
		}
		context = {
			'name': name,
			'lang': self.language[:2],
			'tags': dumps(tags_info),
		}
		return widget + mark_safe(render_to_string('widgets/editor.html', context))

	def value_from_datadict(self, data, files, name):
		text = data.get(name)
		if not text:
			return (None, text)
		fmt = data.get(name + "_format")
		return (fmt, text)
