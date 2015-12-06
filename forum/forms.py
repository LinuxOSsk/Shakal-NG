# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.forms import ModelChoiceField
from django.forms.widgets import RadioSelect
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from .models import Topic, Section
from antispam.forms import AntispamFormMixin
from attachment.forms import AttachmentFormMixin
from common_utils.forms import AuthorsNameFormMixin


COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)


class DescriptionRadioSelect(RadioSelect):
	def render(self, name, value, attrs=None, choices=()):
		queryset = self.choices.queryset #pylint: disable=no-member
		ctx = {
			'name': name,
			'value': value,
			'attrs': attrs,
			'choices': choices,
			'queryset': queryset,
		}
		return mark_safe(render_to_string("includes/description_radio_select.html", ctx))


class TopicForm(AntispamFormMixin, AuthorsNameFormMixin, AttachmentFormMixin, forms.ModelForm):
	section = ModelChoiceField(Section.objects.all(), empty_label=None, widget=DescriptionRadioSelect(), label='Sekcia')

	def get_model(self):
		return Topic

	def security_errors(self):
		return []

	class Meta:
		model = Topic
		fields = ('section', 'authors_name', 'title', 'original_text', )
