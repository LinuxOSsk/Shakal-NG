# -*- coding: utf-8 -*-
from django.forms.widgets import RadioSelect
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class DescriptionRadioSelect(RadioSelect):
	def render(self, name, value, attrs=None, choices=(), *args, **kwargs):
		queryset = self.choices.queryset #pylint: disable=no-member
		ctx = {
			'name': name,
			'value': value,
			'attrs': attrs,
			'choices': choices,
			'queryset': queryset,
		}
		return mark_safe(render_to_string('widgets/description_radio_select.html', ctx))
