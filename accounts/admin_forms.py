# -*- coding: utf-8 -*-
import re

from django import forms
from django.contrib.auth.forms import UserChangeForm as OrigUserChangeForm, UserCreationForm as OrigUserCreationForm
from django.utils.translation import ugettext_lazy as _

from common_utils.admin_widgets import DateTimeInput, EnclosedInput


def get_username_field():
	return forms.RegexField(
		label=_('Username'),
		max_length=30,
		min_length=3,
		regex=re.compile(r'^([\w]+[ ]?)*[\w]$', re.UNICODE),
		help_text=_('Required. Length 3 - 30 characters.'),
		error_message=_('This value must contain spaces oly in the middle.'))


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
