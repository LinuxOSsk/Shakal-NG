# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm as OrigUserChangeForm, UserCreationForm as OrigUserCreationForm
from django.utils.translation import ugettext_lazy as _
from common_utils.admin_widgets import DateTimeInput, EnclosedInput
from rich_editor.forms import RichTextField
from rich_editor import get_parser
import re
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class AuthenticationRememberForm(AuthenticationForm):
	remember_me = forms.BooleanField(label=_('Remember me'), initial=False, required=False)


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
			'last_login': DateTimeInput,
			'date_joined': DateTimeInput,
			'email': EnclosedInput(append='icon-envelope'),
		}


class UserChangeForm(OrigUserChangeForm):
	username = get_username_field()


class ProfileEditForm(forms.ModelForm):
	current_password = forms.CharField(max_length=65536, widget=forms.PasswordInput, label=_('Current password'))
	signature = RichTextField(parser=get_parser('signature'), required=False, max_length=150, widget=forms.TextInput)

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
		self.fields['email'].help_text = mark_safe(_('E-mail address can be changed <a href="{0}">this link</a>.').format(reverse('auth_email_change'))) # pylint: disable=E1101
		self.fields['first_name'].required = False
		self.fields['last_name'].required = False
		self.fields['email'].required = False
		self.fields['original_info'].widget.attrs['js'] = True

	def clean_current_password(self):
		if not self.instance.check_password(self.cleaned_data['current_password']):
			raise ValidationError(_('Please enter the correct password.'))

	def clean_email(self):
		return self.instance.email


class EmailChangeForm(forms.ModelForm):
	current_password = forms.CharField(max_length=65536, widget=forms.PasswordInput, label=_('Current password'))
	email = forms.EmailField(label=_('New e-mail'))
#
	class Meta:
		model = get_user_model()
		fields = (
			'current_password',
			'email',
		)
