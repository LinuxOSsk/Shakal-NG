# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model
from django.core import validators

from web.middlewares.threadlocal import get_current_request


USERNAME_VALIDATOR = validators.RegexValidator(r'^[\w.@+-]+$', 'Meno môže obsahovať len alfanumerické znaky, čísla a znaky @/./+/-/_.', 'invalid')


class AuthorsNameFormMixin(object):
	authors_name_field = 'authors_name'
	author_field = 'author'

	def __init__(self, *args, **kwargs):
		super(AuthorsNameFormMixin, self).__init__(*args, **kwargs)
		request = get_current_request()
		authors_name_field = self.authors_name_field
		if request.user.is_authenticated:
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

	def clean(self):
		authors_name_field = self.authors_name_field
		cleaned_data = super(AuthorsNameFormMixin, self).clean()
		if self.authors_name_field in cleaned_data:
			duplicat_username = (get_user_model().objects
				.filter(username=cleaned_data[authors_name_field])
				.exists())
			if duplicat_username:
				self.add_error(authors_name_field, 'Používateľ s takýmto menom už existuje')
		return cleaned_data

	def save(self, commit=True):
		obj = super(AuthorsNameFormMixin, self).save(commit=False)
		request = get_current_request()
		if request.user.is_authenticated:
			username = get_current_request().user.get_full_name()
			setattr(obj, self.authors_name_field, username)
			if self.author_field:
				setattr(obj, self.author_field, request.user)
		if commit:
			obj.save()
		return obj


class SetRequiredFieldsMixin(object):
	required_fields = {}

	def __init__(self, *args, **kwargs):
		super(SetRequiredFieldsMixin, self).__init__(*args, **kwargs)
		for fieldname, is_required in self.required_fields.items():
			self.fields[fieldname].required = is_required


class SetWidgetAttrsMixin(object):
	widget_attrs = {}

	def __init__(self, *args, **kwargs):
		super(SetWidgetAttrsMixin, self).__init__(*args, **kwargs)
		for fieldname, attrs in self.widget_attrs.items():
			self.fields[fieldname].widget.attrs.update(attrs)
