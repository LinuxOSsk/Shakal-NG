# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserChangeForm as OrigUserChangeForm, UserCreationForm as OrigUserCreationForm

from common_utils.admin_widgets import EnclosedInput


def get_username_field():
	return forms.CharField(
		label='Používateľské meno',
		max_length=150,
		min_length=1,
		help_text='Povinné. Dĺžka 3 - 150 znakov.',
	)


class UserCreationForm(OrigUserCreationForm):
	username = get_username_field()

	class Meta(OrigUserCreationForm.Meta):
		widgets = {
			'email': EnclosedInput(append='fa-envelope'),
		}


class UserChangeForm(OrigUserChangeForm):
	username = get_username_field()

	class Meta(OrigUserChangeForm.Meta):
		widgets = {
			'email': EnclosedInput(append='fa-envelope'),
		}
