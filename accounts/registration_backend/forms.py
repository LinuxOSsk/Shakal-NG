# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm as OriginalAuthenticationForm, PasswordChangeForm as OriginalPasswordChangeForm, PasswordResetForm as OriginalPasswordResetForm, SetPasswordForm as OriginalSetPasswordForm
from django.utils.translation import ugettext_lazy as _

from antispam.forms import AntispamFormMixin


class AuthenticationForm(OriginalAuthenticationForm):
	pass


class UserRegistrationForm(AntispamFormMixin, forms.ModelForm):
	password1 = forms.CharField(widget=forms.PasswordInput, label=_("Password"))
	password2 = forms.CharField(widget=forms.PasswordInput, label=_("Password (again)"))

	def __init__(self, *args, **kwargs):
		super(UserRegistrationForm, self).__init__(*args, **kwargs)
		self.fields['email'].required = True

	class Meta:
		model = get_user_model()
		fields = ["username", "email"]

	def clean_email(self):
		if get_user_model().objects.filter(email__iexact=self.cleaned_data['email']):
			raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
		return self.cleaned_data['email']

	def clean(self):
		super(UserRegistrationForm, self).clean()
		if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
			if self.cleaned_data['password1'] != self.cleaned_data['password2']:
				raise forms.ValidationError(_("The two password fields didn't match."))
		return self.cleaned_data


class PasswordChangeForm(OriginalPasswordChangeForm):
	pass


class PasswordResetForm(OriginalPasswordResetForm):
	pass


class SetPasswordForm(OriginalSetPasswordForm):
	pass
