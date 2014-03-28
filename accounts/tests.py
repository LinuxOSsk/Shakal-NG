# -*- coding: utf-8 -*-
from django.test import TestCase
from accounts.registration_backend.forms import UserRegistrationForm
from .forms import UserCreationForm


USER_FORM_DATA = {
	'username': 'user',
	'email': 'user@user.com',
	'password1': 'P4ssw0rd',
	'password2': 'P4ssw0rd',
}


class RegistrationFormTest(TestCase):
	fixtures = ['users.json']

	def test_form_ok(self):
		form = UserRegistrationForm(USER_FORM_DATA)
		self.assertTrue(form.is_valid())

	def test_unique_email(self):
		data = USER_FORM_DATA.copy()
		data['email'] = "admin@example.com"
		form = UserRegistrationForm(data)
		self.assertFalse(form.is_valid())

	def test_unique_username(self):
		data = USER_FORM_DATA.copy()
		data['username'] = "admin"
		form = UserRegistrationForm(data)
		self.assertFalse(form.is_valid())

	def test_bad_password(self):
		data = USER_FORM_DATA.copy()
		data['password2'] = "bad"
		form = UserRegistrationForm(data)
		self.assertFalse(form.is_valid())


class UserAdminFormTest(TestCase):
	def test_ok(self):
		form = UserCreationForm(USER_FORM_DATA)
		self.assertTrue(form.is_valid())

	def test_bad_username(self):
		data = USER_FORM_DATA.copy()
		data['username'] = 'test@example.com'
		form = UserCreationForm(data)
		self.assertFalse(form.is_valid())
