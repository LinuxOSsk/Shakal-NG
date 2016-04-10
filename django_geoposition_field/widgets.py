# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.template.loader import render_to_string
from django.utils import six
from django.utils.safestring import mark_safe


class GeopositionWidget(forms.MultiWidget):
	def __init__(self, attrs=None):
		widgets = (
			forms.TextInput(),
			forms.TextInput(),
		)
		super(GeopositionWidget, self).__init__(widgets, attrs)

	def decompress(self, value):
		if isinstance(value, six.text_type):
			return value.rsplit(',')
		if value:
			return [value.latitude, value.longitude]
		return [None,None]

	def format_output(self, rendered_widgets):
		return render_to_string('geoposition/widgets/geoposition.html', {
			'latitude_widget': mark_safe(rendered_widgets[0]),
			'longitude_widget': mark_safe(rendered_widgets[1]),
		})

	def render(self, name, value, attrs=None):
		rendered = super(GeopositionWidget, self).render(name, value, attrs)
		return render_to_string('geoposition/widgets/geoposition_container.html', {
			'widget': mark_safe(rendered),
			'name': name,
		})

	class Media:
		js = ('geoposition/geoposition.js',)
		css = {'all': ('geoposition/geoposition.css',)}
