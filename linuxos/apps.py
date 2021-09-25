# -*- coding: utf-8 -*-
from django.apps import AppConfig


class LinuxosConfig(AppConfig):
	name = 'linuxos'
	verbose_name = 'LinuxOS'

	def ready(self):
		from django.contrib import admin
		from .form_fields import PresentationImageFormField

		old_formfield_for_foreignkey = admin.ModelAdmin.formfield_for_foreignkey

		def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
			field = old_formfield_for_foreignkey(self, db_field, request=request, **kwargs)
			if isinstance(field, PresentationImageFormField) and request is not None:
				field.filter_uploads(request.resolver_match.kwargs.get('object_id'))
			return field

		admin.ModelAdmin.formfield_for_foreignkey = formfield_for_foreignkey
