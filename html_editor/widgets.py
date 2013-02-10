# -*- coding: utf-8 -*-

from django.conf import settings
from django.forms import Textarea
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.simplejson import dumps
from html_editor.parser import ALL_TAGS

class HtmlEditor(Textarea):
	class Media:
		js = [
			'js/htmleditor/editor.js',
		]
		css = {
			'all': ('js/wymeditor/skins/shakal/skin.css', )
		}

	def __init__(self, attrs = {}, **kwargs):
		self.language = settings.LANGUAGE_CODE
		attrs.update({'class': 'wymeditor'})
		super(HtmlEditor, self).__init__(attrs)

	def render(self, name, value, attrs = None, **kwargs):
		supported_tags = self.attrs.pop('supported_tags', {})
		widget = mark_safe(u'<div class="textareawrapper">') + super(HtmlEditor, self).render(name, value, attrs) + mark_safe(u'</div>')
		self.attrs['supported_tags'] = supported_tags;
		unsupported_tags = set(ALL_TAGS) - set(supported_tags.keys()) - set(('html', 'body'))
		defined_tags = set(supported_tags.keys()) - set('')
		for tag in supported_tags:
			if tag == '':
				tag_name = 'body'
			else:
				tag_name = tag
			unsupported_tags.update([tag_name + ' > ' + t for t in defined_tags - supported_tags[tag].get_child_tags() if t != ''])
		context = {
			'name': name,
			'lang': self.language[:2],
			'unsupported_tags': dumps(list(unsupported_tags)),
		}
		return widget + mark_safe(render_to_string('widgets/editor.html', context))
