# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.auth import get_user_model
from django.core import validators

from common_utils.middlewares.ThreadLocal import get_current_request


USERNAME_VALIDATOR = validators.RegexValidator(r'^[\w.@+-]+$', 'Meno môže obsahovať len alfanumerické znaky, čísla a znaky @/./+/-/_.', 'invalid')


class AuthorsNameFormMixin(object):
	authors_name_field = 'authors_name'

	def __init__(self, *args, **kwargs):
		super(AuthorsNameFormMixin, self).__init__(*args, **kwargs)
		request = get_current_request()
		authors_name_field = self.get_authors_name_field()
		if request.user.is_authenticated():
			if authors_name_field in self.fields:
				del self.fields[authors_name_field]
		else:
			if not authors_name_field in self.fields:
				self.fields[authors_name_field] = forms.CharField(
					max_length=30,
					validators=[USERNAME_VALIDATOR]
				)
			else:
				self.fields[authors_name_field].required = True
				self.fields[authors_name_field].validators = [USERNAME_VALIDATOR]

	def get_authors_name_field(self):
		return self.authors_name_field

	def clean(self):
		cleaned_data = super(AuthorsNameFormMixin, self).clean()
		authors_name = self.get_authors_name_field()
		if authors_name in cleaned_data:
			if get_user_model().objects.filter(username=cleaned_data[authors_name]).exists():
				self.add_error(authors_name, 'Používateľ s takýmto menom už existuje')
		return cleaned_data

	def save(self, commit=True):
		obj = super(AuthorsNameFormMixin, self).save(commit=False)
		if commit:
			authors_name_field = self.get_authors_name_field()
			cleaned_data = self.cleaned_data
			if not authors_name_field in cleaned_data:
				setattr(obj, authors_name_field, get_current_request().user.get_full_name())
			obj.save()
		return obj
