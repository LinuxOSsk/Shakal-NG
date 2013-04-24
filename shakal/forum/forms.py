# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.forms import ChoiceField, ModelChoiceField
from django.forms.models import ModelChoiceIterator
from django.forms.widgets import HiddenInput, RadioSelect, RadioFieldRenderer, RadioInput
from django.template.defaultfilters import capfirst
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from antispam.forms import AntispamModelFormMixin
from attachment.fields import AttachmentField
from attachment.forms import AttachmentFormMixin
from rich_editor.fields import RichTextField
from models import Topic, Section


COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)


class SectionChoiceIterator(ModelChoiceIterator):
	def choice(self, obj):
		return (self.field.prepare_value(obj), self.field.label_from_instance(obj), obj.description)


class SectionModelChoiceField(ModelChoiceField):
	def _get_choices(self):
		return SectionChoiceIterator(self)
	choices = property(_get_choices, ChoiceField._set_choices)


class SectionRenderer(RadioFieldRenderer):
	def render_choice(self, idx):
		choice = self.choices[idx]
		return mark_safe(force_unicode(RadioInput(self.name, self.value, self.attrs.copy(), choice, idx)) + '<p class="radio-description">' + force_unicode(escape(choice[2])) + '</p>')

	def __iter__(self):
		for idx, choice in enumerate(self.choices):
			yield self.render_choice(idx)

	def __getitem__(self, idx):
		return self.render_choice(idx)


class TopicForm(AntispamModelFormMixin, forms.ModelForm, AttachmentFormMixin):
	section = SectionModelChoiceField(Section.objects.all(), empty_label=None, widget = RadioSelect(renderer = SectionRenderer), label = capfirst(_('section')))
	text = RichTextField(label = _("Text"), max_length = COMMENT_MAX_LENGTH)
	attachment = AttachmentField(label = _("Attachment"), required = False)
	upload_session = forms.CharField(label = "Upload session", widget = HiddenInput, required = False)

	def __init__(self, *args, **kwargs):
		logged = kwargs.pop('logged', False)
		request = kwargs.pop('request')
		super(TopicForm, self).__init__(*args, **kwargs)
		if logged:
			del(self.fields['authors_name'])
			del(self.fields['captcha'])
		self.process_antispam(request)
		self.process_attachments()

	def get_model(self):
		return Topic

	def security_errors(self):
		return []

	class Meta:
		model = Topic
		exclude = ('author', 'created', )
		fields = ('section', 'authors_name', 'title', 'text', )
