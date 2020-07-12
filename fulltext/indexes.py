# -*- coding: utf-8 -*-
from django.db.models.fields import NOT_PROVIDED
from django.template.loader import render_to_string


class SearchField(object):
	name = None

	def get_model_field(self):
		return None

	def get_value(self, obj):
		raise NotImplementedError()


class ModelField(SearchField):
	def __init__(self, model_field):
		self.__model_field = model_field

	def get_model_field(self):
		return self.__model_field

	def get_value(self, obj):
		value = getattr(obj, self.__model_field, None)
		if value is None:
			field = obj.__class__._meta.get_field(self.__model_field)
			if not field.null:
				if field.default == NOT_PROVIDED:
					value = ''
				else:
					value = field.default
		return value


class TemplateField(ModelField):
	def __init__(self, model_field=None):
		self.__model_field = model_field

	def get_template_name(self, obj):
		meta = obj.__class__._meta
		return f'fulltext/{meta.app_label}/{meta.model_name}_{self.name}.txt';

	def get_value(self, obj):
		ctx = {}
		if self.__model_field:
			ctx['document_field'] = self.__model_field
		ctx['object'] = obj
		return render_to_string(self.get_template_name(obj), ctx)


class SearchIndexMeta(type):
	def __new__(cls, name, bases, dct):
		cls_instance = super().__new__(cls, name, bases, dct)
		for name, field in dct.items():
			if not isinstance(field, SearchField):
				continue
			field.name = name
		return cls_instance


class SearchIndex(object, metaclass=SearchIndexMeta):
	register = None
	model = None

	def get_model(self):
		return self.model

	def get_index_queryset(self, using=None):
		return self.get_model()._default_manager.using(using)

	def get_index(self, obj):
		instance = self.register.index_class()
		for instance_key, field in self.__class__.__dict__.items():
			if not isinstance(field, SearchField):
				continue
			setattr(instance, instance_key, field.get_value(obj))
		return instance
