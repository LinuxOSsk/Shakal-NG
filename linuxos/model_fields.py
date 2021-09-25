# -*- coding: utf-8 -*-
from django.db import models

from .form_fields import PresentationImageFormField


class PresentationImageField(models.ForeignKey):
	def __init__(self, **kwargs):
		kwargs.setdefault('to', 'attachment.attachmentimage')
		kwargs.setdefault('blank', True)
		kwargs.setdefault('null', True)
		kwargs.setdefault('on_delete', models.SET_NULL)
		super().__init__(**kwargs)

	def deconstruct(self, *args, **kwargs):
		name, path, args, kwargs = super().deconstruct()
		if kwargs.get('to') == 'attachment.attachmentimage':
			del kwargs['to']
		if kwargs.get('blank') is True:
			del kwargs['blank']
		if kwargs.get('null') is True:
			del kwargs['null']
		if kwargs.get('on_delete') == models.SET_NULL:
			del kwargs['on_delete']
		return name, path, args, kwargs

	def formfield(self, *, using=None, **kwargs):
		return super().formfield(**{
			'form_class': PresentationImageFormField,
			'queryset': self.remote_field.model._default_manager.using(using).select_related('attachment_ptr').order_by('object_id', 'pk'),
			'model': self.model,
			'to_field_name': self.remote_field.field_name,
			**kwargs,
			'blank': self.blank,
		})
