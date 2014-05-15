# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.forms import FileField
from django.forms.widgets import ClearableFileInput
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


class AttachmentWidget(ClearableFileInput):
	def render(self, name, value, attrs = None):
		max_size = self.attrs.pop('max_size', -1)
		widget = super(AttachmentWidget, self).render(name, value, attrs)
		if max_size >= 0:
			widget += mark_safe(
				"<p class='help upload_size'>" +
				_("Maximum size is: ") +
				filesizeformat(max_size) +
				"</p>")
		self.attrs['max_size'] = max_size
		return widget


class AttachmentField(FileField):
	widget = AttachmentWidget

	def clean(self, data, initial=None):
		size = 0 if data.size is None else data.size
		if self.widget.attrs.get('max_size', -1) >= 0:
			if size > self.widget.attrs['max_size']:
				raise ValidationError(
					_('File size exceeded, maximum size is ') +
					filesizeformat(self.widget.attrs['max_size']))
		return super(AttachmentField, self).clean(data, initial)
