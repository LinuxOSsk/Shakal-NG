# -*- coding: utf-8 -*-
from allauth.account import app_settings
from allauth.account.forms import LoginForm as CoreLoginForm, AddEmailForm as CoreAddEmailForm, SignupForm as CoreSignupForm, PasswordField
from allauth.account.utils import perform_login
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.safestring import mark_safe

from .auth_remember_utils import remember_user
from antispam.forms import AntispamFormMixin
from rich_editor import get_parser
from rich_editor.forms import RichTextField


class ProfileEditForm(forms.ModelForm):
	current_password = forms.CharField(max_length=65536, widget=forms.PasswordInput, label='Súčasné heslo')
	signature = RichTextField(parser=get_parser('signature'), required=False, max_length=150, widget=forms.TextInput, label='Podpis')

	class Meta:
		model = get_user_model()
		fields = (
			'current_password',
			'first_name',
			'last_name',
			'jabber',
			'url',
			'signature',
			'email',
			'display_mail',
			'distribution',
			'original_info',
			'year',
		)

	def __init__(self, *args, **kwargs):
		super(ProfileEditForm, self).__init__(*args, **kwargs)
		self.fields['email'].widget.attrs['readonly'] = True
		self.fields['email'].help_text = mark_safe('E-mailová adresa sa dá zmeniť <a href="{0}">tu</a>.').format(reverse('account_email'))
		self.fields['first_name'].required = False
		self.fields['last_name'].required = False
		self.fields['email'].required = False
		self.fields['original_info'].widget.attrs['js'] = True

	def clean_current_password(self):
		if not self.instance.check_password(self.cleaned_data['current_password']):
			raise ValidationError('Zadajte prosím správne heslo.')

	def clean_email(self):
		return self.instance.email


class AvatarUpdateForm(forms.ModelForm):
	class Meta:
		model = get_user_model()
		fields = ('avatar',)


class PositionUpdateForm(forms.ModelForm):
	no_compress = True

	class Meta:
		model = get_user_model()
		fields = ('geoposition',)


class EmailChangeForm(forms.ModelForm):
	current_password = forms.CharField(max_length=65536, widget=forms.PasswordInput, label='Súčasné heslo')
	email = forms.EmailField(label='Nový e-mail')

	class Meta:
		model = get_user_model()
		fields = (
			'current_password',
			'email',
		)


class LoginForm(CoreLoginForm):
	def login(self, request, redirect_url=None):
		ret = perform_login(request, self.user, email_verification=app_settings.EMAIL_VERIFICATION, redirect_url=redirect_url) #pylint: disable=no-member
		remember = app_settings.SESSION_REMEMBER #pylint: disable=no-member
		if remember is None:
			remember = self.cleaned_data['remember']
		if remember:
			return remember_user(ret, self.user)
		return ret


class AddEmailForm(CoreAddEmailForm):
	oldpassword = PasswordField(label='Súčasné heslo')

	def clean_oldpassword(self):
		if not self.user.check_password(self.cleaned_data.get("oldpassword")):
			raise forms.ValidationError("Zadajte prosím súčasné heslo")
		return self.cleaned_data["oldpassword"]


class SignupForm(AntispamFormMixin, CoreSignupForm):
	pass
