# -*- coding: utf-8 -*-
from django.db.models import signals
from django.db.models.fields import TextField
from .forms import RichTextField
from .parser import HtmlParser


class RichTextOriginalField(TextField):
	widget = RichTextField

	def to_python(self, value):
		print(type(value))
		return value

	def get_prep_value(self, value):
		return u":".join(value)


class RichTextFilteredField(TextField):
	def __init__(self, original_field, property_name, parser = HtmlParser, *args, **kwargs):
		super(RichTextFilteredField, self).__init__(*args, **kwargs)
		self.original_field = original_field
		self.property_name = property_name
		self.parser = parser()

	def contribute_to_class(self, cls, name):
		signals.pre_save.connect(self.update_filtered_field, sender = cls)
		signals.post_init.connect(self.save_old_value, sender = cls)
		self.create_filtered_property(cls, name)
		super(RichTextFilteredField, self).contribute_to_class(cls, name)

	def update_filtered_field(self, instance, **kwargs):
		self.parser.parse(getattr(instance, self.original_field))
		parsed_text = self.parser.get_output()
		setattr(instance, self.name, parsed_text)

	def save_old_value(self, instance, **kwargs):
		old_values = getattr(instance, "old_values", {})
		old_values[self.original_field] = getattr(instance, self.original_field)
		setattr(instance, "old_values", old_values)

	def create_filtered_property(self, cls, field_name):
		original_field = self.original_field
		parser = self.parser

		def filtered_property(self):
			old_values = getattr(self, "old_values", {})
			old_field_value = old_values.get(original_field, (None, ''))
			print(getattr(self, original_field)[1])
			if getattr(self, original_field) != old_field_value:
				parser.parse(getattr(self, original_field)[1])
				parsed = parser.get_output()
				old_values[field_name] = parsed
				setattr(self, field_name, parsed)
			return getattr(self, field_name)

		setattr(cls, self.property_name, property(filtered_property))
