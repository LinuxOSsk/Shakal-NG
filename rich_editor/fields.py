# -*- coding: utf-8 -*-
from django.db.models import signals, TextField, SubfieldBase, Field

from .forms import RichOriginalField
from .parser import HtmlParser


class RichTextOriginalField(Field):
	__metaclass__ = SubfieldBase

	def get_internal_type(self):
		return "TextField"

	def formfield(self, **kwargs):
		defaults = {
			'form_class': RichOriginalField,
			'js': False,
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
		return value[0] + u":" + value[1]


class RichTextFilteredField(TextField):
	def __init__(self, original_field, property_name, parsers = {'html': HtmlParser()}, *args, **kwargs):
		super(RichTextFilteredField, self).__init__(*args, **kwargs)
		self.original_field = original_field
		self.property_name = property_name
		self.parsers = parsers

	def contribute_to_class(self, cls, name):
		signals.pre_save.connect(self.update_filtered_field, sender = cls)
		signals.post_init.connect(self.save_old_value, sender = cls)
		self.create_filtered_property(cls, name)
		super(RichTextFilteredField, self).contribute_to_class(cls, name)

	def update_filtered_field(self, instance, **kwargs):
		setattr(instance, self.name, self.filter_data(getattr(instance, self.original_field)))

	def filter_data(self, data):
		fmt, value = data
		if not fmt:
			return data
		parser = self.parsers[fmt]
		parser.parse(value)
		return parser.get_output()

	def save_old_value(self, instance, **kwargs):
		old_values = getattr(instance, "old_values", {})
		old_values[self.original_field] = getattr(instance, self.original_field)
		setattr(instance, "old_values", old_values)

	def create_filtered_property(self, cls, field_name):
		original_field = self.original_field
		parsers = self.parsers

		def filtered_property(self):
			old_values = getattr(self, "old_values", {})
			old_field_value = old_values.get(original_field, ('html', ''))
			if getattr(self, original_field) != old_field_value:
				fmt, value = getattr(self, original_field)
				parser = parsers[fmt]
				parser.parse(value)
				parsed = parser.get_output()
				old_values[field_name] = parsed
				setattr(self, field_name, parsed)
			return getattr(self, field_name)

		setattr(cls, self.property_name, property(filtered_property))
