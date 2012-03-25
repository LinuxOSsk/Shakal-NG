# -*- coding: utf-8 -*-
from django.conf import settings
from django.forms import Textarea
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

class HtmlEditor(Textarea):
	class Media:
		js = [
			'http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.js',
			'js/wymeditor/jquery.wymeditor.min.js',
		]

	def __init__(self, attrs = None, **kwargs):
		self.language = getattr(settings, 'LANGUAGE_CODE')
		if attrs:
			attrs.update({'class': 'wymeditor'})
		else:
			attrs = {'class': 'wymeditor'}
		super(HtmlEditor, self).__init__(attrs = attrs)

	def render(self, name, value, attrs = None, **kwargs):
		widget = super(HtmlEditor, self).render(name, value, attrs)
		context = {
			'name': name,
			'lang': self.language[:2],
		}
		return widget + mark_safe(render_to_string('widgets/wymeditor.html', context))
