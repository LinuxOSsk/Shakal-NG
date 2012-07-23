# -*- coding: utf-8 -*-

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.forms import ValidationError, BooleanField, CharField, RegexField, ModelForm
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
			help_text = _('Required. 30 characters or fewer.'),
			error_message = _('This value must contain spaces oly in the middle.'))


class LessRestrictiveUserCreationForm(UserCreationForm, LessRestrictiveUserEditFormMixin):
	username = LessRestrictiveUserEditFormMixin.get_username_field()


class LessRestrictiveUserChangeForm(UserChangeForm, LessRestrictiveUserEditFormMixin):
	username = LessRestrictiveUserEditFormMixin.get_username_field()


class ProfileEditForm(ModelForm):
	first_name = CharField(max_length = 30, required = False)
	last_name = CharField(max_length = 30, required = False)

	class Meta:
		model = UserProfile
		exclude = ('user', )
		fields = ('first_name', 'last_name', 'jabber', 'url', 'signature', 'display_mail', 'distribution', 'info', 'year', )

	def __init__(self, *args, **kwargs):
		if 'instance' in kwargs:
			user = kwargs['instance'].user
			kwargs['initial'] = {
				'first_name': user.first_name,
				'last_name': user.last_name,
			}
		super(ProfileEditForm, self).__init__(*args, **kwargs)
