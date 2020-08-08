# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.db.models.fields import NOT_PROVIDED
from django.template.loader import render_to_string

from comments.models import Comment


User = get_user_model()


class SearchField(object):
	name = None

	def get_model_field(self):
		return None

	def get_value(self, obj):
		raise NotImplementedError()


class ModelField(SearchField):
	def __init__(self, model_field):
		self._model_field = model_field

	def get_model_field(self):
		return self._model_field

	def get_value(self, obj):
		field_split = self._model_field.split('__')
		for subfield in field_split[:-1]:
			obj = getattr(obj, subfield)
			if obj is None:
				return None
		field_split = field_split[-1]

		value = getattr(obj, field_split, None)
		if value is None:
			field = obj.__class__._meta.get_field(field_split)
			if not field.null:
				if field.default == NOT_PROVIDED:
					value = ''
				else:
					value = field.default
		return value


class TemplateField(ModelField):
	def __init__(self, model_field=None):
		super().__init__(model_field)

	def get_template_name(self, obj):
		meta = obj.__class__._meta
		return f'fulltext/{meta.app_label}/{meta.model_name}_{self.name}.txt';

	def get_context_data(self, obj):
		ctx = {}
		if self._model_field:
			ctx['document_field'] = self._model_field
		ctx['object'] = obj
		return ctx

	def get_value(self, obj):
		return render_to_string(self.get_template_name(obj), self.get_context_data(obj))


class CommentsField(TemplateField):
	def __init__(self):
		super().__init__()

	def get_context_data(self, obj):
		return {'comments': obj.comments.all()}

	def get_template_name(self, obj):
		return f'fulltext/comments/comments.txt';


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

	def get_language_code(self, obj): # pylint: disable=unused-argument
		return settings.LANGUAGE_CODE

	def get_index(self, obj):
		instance = self.register.index_class()
		instance.language_code = self.get_language_code(obj)
		for instance_key, field in self.__class__.__dict__.items():
			if not isinstance(field, SearchField):
				continue
			setattr(instance, instance_key, field.get_value(obj))
		return instance


class CommentsPrefetch(Prefetch):
	def __init__(self, lookup=None, queryset=None, **kwargs):
		lookup = lookup or 'comments'
		if queryset is None:
			queryset = (Comment.objects.only(
				'pk', 'object_id', 'content_type_id', 'parent_id',
				'subject', 'filtered_comment', 'is_public', 'is_removed'
			))
		super().__init__(lookup, queryset=queryset, **kwargs)


class AuthorPrefetch(Prefetch):
	def __init__(self, lookup=None, queryset=None, **kwargs):
		lookup = lookup or 'author'
		if queryset is None:
			queryset = (User.objects.only(
				'pk', 'avatar', 'first_name', 'last_name', 'username',
			))
		super().__init__(lookup, queryset=queryset, **kwargs)
