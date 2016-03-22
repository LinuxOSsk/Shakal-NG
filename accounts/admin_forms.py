# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django import forms
from django.contrib.auth.forms import UserChangeForm as OrigUserChangeForm, UserCreationForm as OrigUserCreationForm

from common_utils.admin_widgets import DateTimeInput, EnclosedInput


def get_username_field():
	return forms.RegexField(
		label='Používateľské meno',
		max_length=30,
		min_length=3,
		regex=re.compile(r'^([\w]+[ ]?)*[\w]$', re.UNICODE),
		help_text='Povinné. Dĺžka 3 - 30 znakov.',
		error_message='Toto pole môže obsahovať maximálne jednu medzeru v strede.')


class UserCreationForm(OrigUserCreationForm):
	username = get_username_field()

	class Meta(OrigUserCreationForm.Meta):
		widgets = {
			'email': EnclosedInput(append='icon-envelope'),
		}


class UserChangeForm(OrigUserChangeForm):
	username = get_username_field()

	class Meta(OrigUserChangeForm.Meta):
		widgets = {
			'last_login': DateTimeInput,
			'date_joined': DateTimeInput,
			'email': EnclosedInput(append='icon-envelope'),
		}
