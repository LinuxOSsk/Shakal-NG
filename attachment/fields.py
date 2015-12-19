# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.forms import FileField
from django.forms.widgets import ClearableFileInput
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


def get_file_list(files, name):
	if hasattr(files, 'getlist'):
		return files.getlist(name)
	else:
		value = files.get(name)
		if isinstance(value, list):
			return value
		elif value is None:
			return value
		else:
			return [value]


class AttachmentWidget(ClearableFileInput):
	def render(self, name, value, attrs=None):
		attrs = attrs or {}
		attrs['multiple'] = 'multiple'
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

	def value_from_datadict(self, data, files, name):
		return get_file_list(files, name)


class AttachmentField(FileField):
	widget = AttachmentWidget

	def clean(self, data, initial=None):
		if isinstance(data, list):
			size = sum(0 if f is None else f.size for f in data)
		else:
			size = 0 if data is None else data.size

		if self.widget.attrs.get('max_size', -1) >= 0:
			if size > self.widget.attrs['max_size']:
				raise ValidationError(
					_('File size exceeded, maximum size is ') +
					filesizeformat(self.widget.attrs['max_size']))

		return data

	def to_python(self, data):
		ret = []
		for item in data:
			f = super(AttachmentField, self).to_python(item)
			if f:
				ret.append(f)
		return ret
