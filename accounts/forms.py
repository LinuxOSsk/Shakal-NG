# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.core.urlresolvers import reverse
from django.forms import ValidationError, BooleanField, CharField, PasswordInput, RegexField, ModelForm, EmailField, TextInput
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationForm

from antispam.forms import AntispamFormMixin
from rich_editor import get_parser
from rich_editor.forms import RichTextField, RichOriginalField


class RegistrationFormUniqueEmail(RegistrationForm, AntispamFormMixin):
	def __init__(self, request, *args, **kwargs):
		super(RegistrationFormUniqueEmail, self).__init__(*args, **kwargs)
		self.process_antispam(request)

	def clean_email(self):
		if get_user_model().objects.filter(email__iexact = self.cleaned_data['email']):
			raise ValidationError(_("This email address is already in use. Please supply a different email address."))
		return self.cleaned_data['email']


class AuthenticationRememberForm(AuthenticationForm):
	remember_me = BooleanField(label = _('Remember me'), initial = False, required = False)


class LessRestrictiveUserEditFormMixin:
	@staticmethod
	def get_username_field():
		#return CharField(
		#	label = _('Username'),
		#	max_length = 30,
		#	min_length = 3,
		#	help_text = _('Required. Length 3 - 30 characters.'))
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

	def full_clean(self):
		super(LessRestrictiveUserChangeForm, self).full_clean()
		if 'username' in self._errors:
			del self._errors['username']


class ProfileEditForm(ModelForm):
	current_password = CharField(max_length = 128, widget = PasswordInput, label = _('Current password'))
	first_name = CharField(max_length = 30, required = False, label = _('First name'))
	last_name = CharField(max_length = 30, required = False, label = _('Last name'))
	email = EmailField(required = False)
	signature = RichTextField(parser = get_parser('signature'), required = False, max_length = 150, widget = TextInput)
	original_info = RichOriginalField(label = _("Informations"), max_length = 10000, js = True, required = False)

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

	def clean_current_password(self):
		if not self.instance.check_password(self.cleaned_data['current_password']):
			raise ValidationError(_('Please enter the correct password.'))

	def clean_email(self):
		return self.instance.email


class EmailChangeForm(ModelForm):
	current_password = CharField(max_length = 128, widget = PasswordInput, label = _('Current password'))
	email = EmailField(label = _('New e-mail'))

	class Meta:
		model = get_user_model()
		fields = (
			'current_password',
			'email',
		)
