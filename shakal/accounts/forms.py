# -*- coding: utf-8 -*-

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms import ValidationError, BooleanField, CharField, PasswordInput, RegexField, ModelForm, Form, EmailField
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from models import UserProfile
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
			help_text = _('Required. Length 3 - 30 characters.'),
			error_message = _('This value must contain spaces oly in the middle.'))


class LessRestrictiveUserCreationForm(UserCreationForm, LessRestrictiveUserEditFormMixin):
	username = LessRestrictiveUserEditFormMixin.get_username_field()


class LessRestrictiveUserChangeForm(UserChangeForm, LessRestrictiveUserEditFormMixin):
	username = LessRestrictiveUserEditFormMixin.get_username_field()


class ProfileEditForm(ModelForm):
	current_password = CharField(max_length = 128, widget = PasswordInput, label = _('Current password'))
	first_name = CharField(max_length = 30, required = False, label = _('First name'))
	last_name = CharField(max_length = 30, required = False, label = _('Last name'))
	email = EmailField(required = False)

	class Meta:
		model = UserProfile
		exclude = ('user', )
		fields = ('current_password', 'first_name', 'last_name', 'jabber', 'url', 'signature', 'email', 'display_mail', 'distribution', 'info', 'year', )

	def __init__(self, *args, **kwargs):
		if 'instance' in kwargs:
			user = kwargs['instance'].user
			kwargs['initial'] = {
				'first_name': user.first_name,
				'last_name': user.last_name,
				'email': user.email,
			}
		super(ProfileEditForm, self).__init__(*args, **kwargs)
		self.fields['email'].widget.attrs['readonly'] = True
		self.fields['email'].help_text = mark_safe(_('E-mail address can be changed <a href="{0}">this link</a>.').format(reverse('auth_email_change')))

	def clean_current_password(self):
		if not self.instance.user.check_password(self.cleaned_data['current_password']):
			raise ValidationError(_('Please enter the correct password.'))

	def clean_email(self):
		return self.instance.user.email

	def save(self, commit = True):
		user_profile = super(ProfileEditForm, self).save(commit)
		user = user_profile.user
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		if commit:
			user.save()


class EmailChangeForm(Form):
	current_password = CharField(max_length = 128, widget = PasswordInput, label = _('Current password'))
	email = EmailField(label = _('New e-mail'))
