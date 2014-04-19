# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms.fields import CharField
from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe


class AntispamInput(TextInput):
	def render(self, name, value, attrs = None):
		if getattr(settings, 'CAPTCHA_DISABLE', False):
			return ''
		question = self.attrs.pop("question", "")
		answer = self.attrs.pop("answer", "")
		data = super(AntispamInput, self).render(name, value, attrs)
		self.attrs['question'] = question
		self.attrs['answer'] = answer
		return mark_safe(u'<span class="question">' + question + u'</span>' + data)


class AntispamField(CharField):
	widget = AntispamInput

	def clean(self, value):
		if getattr(settings, 'CAPTCHA_DISABLE', False):
			return ''
		value = super(AntispamField, self).clean(value)
		if value != self.widget.attrs.get("answer", ""):
			raise ValidationError(u"Nesprávna odpoveď.")
		return value
