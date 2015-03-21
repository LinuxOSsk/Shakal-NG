# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.forms import ModelChoiceField
from django.forms.widgets import HiddenInput, RadioSelect
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from .models import Topic, Section
from antispam.forms import AntispamFormMixin
from attachment.fields import AttachmentField
from attachment.forms import TemporaryAttachmentFormMixin
from common_utils import get_meta
from common_utils.forms import AuthorsNameFormMixin
from rich_editor.forms import RichOriginalField


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


class TopicForm(AntispamFormMixin, AuthorsNameFormMixin, TemporaryAttachmentFormMixin, forms.ModelForm):
	section = ModelChoiceField(Section.objects.all(), empty_label=None, widget=DescriptionRadioSelect(), label='Sekcia')
	original_text = RichOriginalField(parsers=get_meta(Topic).get_field('original_text').parsers, label='Text', max_length=COMMENT_MAX_LENGTH)
	attachment = AttachmentField(label='Príloha', required=False)
	upload_session = forms.CharField(widget=HiddenInput, required=False)

	def __init__(self, *args, **kwargs):
		super(TopicForm, self).__init__(*args, **kwargs)
		self.process_attachments()

	def get_model(self):
		return Topic

	def security_errors(self):
		return []

	class Meta:
		model = Topic
		exclude = ('author', 'created', )
		fields = ('section', 'authors_name', 'title', 'original_text', )
