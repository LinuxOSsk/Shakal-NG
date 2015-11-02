# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from common_utils.middlewares.ThreadLocal import get_current_request
from django.core import validators


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
					validators=[validators.RegexValidator(r'^[\w.@+-]+$', 'Meno môže obsahovať len alfanumerické znaky, čísla a znaky @/./+/-/_.', 'invalid')]
				)
			else:
				self.fields[authors_name_field].validators = [validators.RegexValidator(r'^[\w.@+-]+$', 'Meno môže obsahovať len alfanumerické znaky, čísla a znaky @/./+/-/_.', 'invalid')]

	def get_authors_name_field(self):
		return self.authors_name_field

	def save(self, commit=True):
		obj = super(AuthorsNameFormMixin, self).save(commit=False)
		if commit:
			authors_name_field = self.get_authors_name_field()
			cleaned_data = self.cleaned_data
			if not authors_name_field in cleaned_data:
				setattr(obj, authors_name_field, get_current_request().user.get_full_name())
			obj.save()
		return obj
