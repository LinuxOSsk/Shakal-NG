# -*- coding: utf-8 -*-

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.forms import ValidationError, BooleanField, RegexField
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationForm


class RegistrationFormUniqueEmail(RegistrationForm):
	def clean_email(self):
		if User.objects.filter(email__iexact=self.cleaned_data['email']):
			raise ValidationError(_("This email address is already in use. Please supply a different email address."))
		return self.cleaned_data['email']


class AuthenticationRememberForm(AuthenticationForm):
	remember_me = BooleanField(label = _('Remember me'), initial = False, required = False)


class LessRestrictiveUserEditFormMixin:
	@staticmethod
	def get_username_field():
		return RegexField(
			label = _('Username'),
			max_length = 30,
			min_length = 3,
			regex = r'^([^\s]+[ ]?)*[^\s]$',
			help_text = _('Required. 30 characters or fewer.'),
			error_message = _('This value must contain spaces oly in the middle.'))


class LessRestrictiveUserCreationForm(UserCreationForm, LessRestrictiveUserEditFormMixin):
	username = LessRestrictiveUserEditFormMixin.get_username_field()


class LessRestrictiveUserChangeForm(UserChangeForm, LessRestrictiveUserEditFormMixin):
	username = LessRestrictiveUserEditFormMixin.get_username_field()
