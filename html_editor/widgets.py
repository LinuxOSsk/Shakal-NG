# -*- coding: utf-8 -*-

from django.conf import settings
from django.forms import Textarea
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

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
		widget = super(HtmlEditor, self).render(name, value, attrs)
		context = {
			'name': name,
			'lang': self.language[:2]
		}
		return widget + mark_safe(render_to_string('widgets/editor.html', context))
