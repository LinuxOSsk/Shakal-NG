# -*- coding: utf-8 -*-
from django.db.models import signals, TextField, SubfieldBase, Field

from .forms import RichOriginalField
from .parser import HtmlParser


class RichTextOriginalField(Field):
	__metaclass__ = SubfieldBase

	def __init__(self, filtered_field, property_name, parsers=None, *args, **kwargs):
		super(RichTextOriginalField, self).__init__(*args, **kwargs)
		self.filtered_field = filtered_field
		self.property_name = property_name
		self.parsers = parsers or {'html': HtmlParser()}

	def deconstruct(self):
		name, path, args, kwargs = super(RichTextOriginalField, self).deconstruct()
		kwargs['filtered_field'] = self.filtered_field
		kwargs['property_name'] = self.property_name
		return name, path, args, kwargs

	def get_internal_type(self):
		return "TextField"

	def formfield(self, **kwargs):
		defaults = {
			'form_class': RichOriginalField,
			'parsers': self.parsers
		}
		defaults.update(kwargs)
		return super(RichTextOriginalField, self).formfield(**defaults)

	def to_python(self, value):
		if not isinstance(value, basestring):
			return value
		if ':' in value:
			return tuple(value.split(":", 1))
		else:
			return ('html', value)

	def get_prep_value(self, value):
		return value[0] + ":" + value[1]

	def contribute_to_class(self, cls, name):
		signals.pre_save.connect(self.update_filtered_field, sender = cls)
		signals.post_init.connect(self.save_old_value, sender = cls)
		self.create_filtered_property(cls, name)
		super(RichTextOriginalField, self).contribute_to_class(cls, name)

	def update_filtered_field(self, instance, **kwargs):
		if not hasattr(instance, "old_values") or not self.name in instance.old_values or instance.old_values[self.name] != getattr(instance, self.name) or not instance.pk:
			setattr(instance, self.filtered_field, self.filter_data(getattr(instance, self.name)))

	def save_old_value(self, instance, **kwargs):
		old_values = getattr(instance, "old_values", {})
		old_values[self.name] = getattr(instance, self.name)
		setattr(instance, "old_values", old_values)

	def create_filtered_property(self, cls, field_name):
		original_field = field_name
		filtered_field = self.filtered_field
		parsers = self.parsers

		def filtered_property(self):
			old_values = getattr(self, "old_values", {})
			old_field_value = old_values.get(original_field, None)
			if old_field_value is not None and getattr(self, original_field) != old_field_value:
				fmt, value = getattr(self, original_field)[:2]
				parser = parsers[fmt]
				parser.parse(value)
				parsed = parser.get_output()
				old_values[original_field] = parsed
				setattr(self, filtered_field, parsed)
			return getattr(self, filtered_field)
		setattr(cls, self.property_name, property(filtered_property))

	def filter_data(self, data):
		if len(data) == 3:
			return data[2]
		fmt, value = data
		if not fmt:
			return data
		parser = self.parsers[fmt]
		parser.parse(value)
		return parser.get_output()


class RichTextFilteredField(TextField):
	def __init__(self, *args, **kwargs):
		kwargs['editable'] = False
		super(RichTextFilteredField, self).__init__(*args, **kwargs)
