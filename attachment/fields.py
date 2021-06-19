# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.forms import FileField, ImageField
from django.forms.widgets import ClearableFileInput
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _


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
	def render(self, name, value, attrs=None, *args, **kwargs):
		attrs = attrs or {}
		max_size = self.attrs.pop('max_size', -1)
		widget = super(AttachmentWidget, self).render(name, value, attrs, *args, **kwargs)
		if max_size >= 0:
			widget += mark_safe(
				"<p class='help upload_size'>" +
				_("Maximum size is: ") +
				filesizeformat(max_size) +
				"</p>")
		self.attrs['max_size'] = max_size
		return widget


class AttachmentWidgetMultiple(AttachmentWidget):
	def render(self, name, value, attrs=None, *args, **kwargs):
		attrs = attrs or {}
		attrs['multiple'] = 'multiple'
		return super(AttachmentWidgetMultiple, self).render(name, value, attrs, *args, **kwargs)

	def value_from_datadict(self, data, files, name):
		return get_file_list(files, name)


class AttachmentField(FileField):
	widget = AttachmentWidget

	def to_python(self, data):
		if isinstance(data, list):
			ret = []
			for item in data:
				f = super(AttachmentField, self).to_python(item)
				if f:
					ret.append(f)
			return ret
		else:
			return super(AttachmentField, self).to_python(data)

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

		if isinstance(data, list):
			return [super(AttachmentField, self).clean(f, initial) for f in data]
		else:
			return super(AttachmentField, self).clean(data, initial)


class AttachmentImageField(AttachmentField, ImageField):
	def clean(self, data, initial=None):
		image_file = super(AttachmentImageField, self).clean(data, initial)
		if image_file.image.size[0] > 8192 or image_file.image.size[1] > 8192:
			raise ValidationError('Prekročený maximálny rozmer obrázka 8192 pixelov.')
		if (image_file.image.size[0] * image_file.image.size[1]) > (1024 * 1024 * 32):
			raise ValidationError('Obrázok je väčší než 32 megapixelov.')
		return image_file


class AttachmentFieldMultiple(AttachmentField):
	widget = AttachmentWidgetMultiple
