# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from rich_editor import get_parser
from rich_editor.forms import RichTextField


class AuthenticationRememberForm(AuthenticationForm):
	remember_me = forms.BooleanField(label=_('Remember me'), initial=False, required=False)


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
		self.fields['email'].help_text = mark_safe(_('E-mail address can be changed <a href="{0}">this link</a>.').format(reverse('auth_email_change')))
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

	class Meta:
		model = get_user_model()
		fields = (
			'current_password',
			'email',
		)
