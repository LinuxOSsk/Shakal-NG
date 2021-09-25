# -*- coding: utf-8 -*-
from django import forms
from django.db import models
from django.db.models import Q
from django.forms.models import ModelChoiceIterator
from django.contrib.contenttypes.models import ContentType


class GroupModelChoiceIterator(ModelChoiceIterator):
	def get_group(self, instance):
		raise NotImplementedError()

	def __format_group(self, current_group, instances):
		if instances:
			if current_group is None:
				yield from instances
			else:
				yield (current_group, instances)

	def __iter__(self):
		if self.field.empty_label is not None:
			yield ("", self.field.empty_label)

		current_group = None
		instances = []
		queryset = self.queryset
		for obj in queryset:
			group = self.get_group(obj)
			if group is not None and group != current_group:
				yield from self.__format_group(current_group, instances)
				current_group = group
				instances = []
			instances.append(self.choice(obj))

		yield from self.__format_group(current_group, instances)


class PresentationImageIterator(GroupModelChoiceIterator):
	def get_group(self, instance):
		return "Globálne" if instance.object_id == 0 else "Nahrané súbory"


class PresentationImageWidget(forms.RadioSelect):
	template_name = 'django/forms/widgets/presentation_image_radio.html'
	option_template_name = 'django/forms/widgets/presentation_image_radio_option.html'

	class Media:
		css = {
			'screen': ('css/common/presentation_image_select.css',)
		}


class PresentationImageFormField(forms.ModelChoiceField):
	iterator = PresentationImageIterator

	def __init__(self, *args, **kwargs):
		kwargs.setdefault('widget', PresentationImageWidget)
		kwargs.setdefault('empty_label', "Automaticky")
		kwargs.setdefault('initial', None)
		self.model = kwargs.pop('model')
		super().__init__(*args, **kwargs)

	def filter_uploads(self, instance):
		if isinstance(instance, models.Model):
			object_id = instance.pk
		else:
			object_id = instance
		q = Q(object_id=0)
		if object_id:
			q = q | Q(object_id=object_id)
		self.queryset = self.queryset.filter(q)

	def get_limit_choices_to(self):
		if not isinstance(self.model, ContentType):
			self.model = ContentType.objects.get_for_model(self.model)
		return {'content_type': self.model}
