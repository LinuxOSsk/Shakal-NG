# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms.fields import CharField
from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe
from fulltext.utils import unaccent


class AntispamInput(TextInput):
	def render(self, name, value, *args, **kwargs):
		if getattr(settings, 'CAPTCHA_DISABLE', False):
			return ''
		question = self.attrs.pop("question", "")
		answer = self.attrs.pop("answer", "")
		data = super().render(name, value, *args, **kwargs)
		self.attrs['question'] = question
		self.attrs['answer'] = answer
		return mark_safe('<span class="question">' + question + '</span>' + data)


class AntispamField(CharField):
	widget = AntispamInput

	def clean(self, value):
		if getattr(settings, 'CAPTCHA_DISABLE', False):
			return ''
		value = super().clean(value)
		answer = self.widget.attrs.get("answer", "")
		if unaccent(value).lower() != unaccent(answer).lower():
			raise ValidationError("Nesprávna odpoveď.")
		return value
