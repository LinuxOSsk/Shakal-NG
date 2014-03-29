# -*- coding: utf-8 -*-
from django.test import TestCase

from .forms import UserCreationForm, ProfileEditForm
from .models import User
from .registration_backend.forms import UserRegistrationForm
from common_utils.tests_common import AdminSiteTestCase, ProcessFormTestMixin


USER_FORM_DATA = {
	'username': 'uniqueuser',
	'email': 'uniqueuser@example.com',
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


class ProfileEditFormTest(ProcessFormTestMixin, TestCase):
	fixtures = ['users.json']

	def get_form_with_password(self, password):
		user = User.objects.get(username="admin")
		form = ProfileEditForm(instance=user)
		data = self.extract_form_data(form)
		data['current_password'] = password
		return ProfileEditForm(data, instance=user)

	def test_ok(self):
		form = self.get_form_with_password("P4ssw0rd")
		self.assertTrue(form.is_valid())

	def test_bad_password(self):
		form = self.get_form_with_password("bad")
		self.assertFalse(form.is_valid())


class AdminUserTest(AdminSiteTestCase):
	model = "user"
	fixtures = ['users.json']

	DEFAULT_ADD_DATA = {
		'username': 'uniquename',
		'email': 'uniquemail@example.com',
		'password1': 'P4ssw0rd',
		'password2': 'P4ssw0rd',
	}

	DEFAULT_DATA = {
		'username': 'username2',
		'email': 'email2@example.com',
	}

	def setUp(self):
		self.login("admin", "P4ssw0rd")

	def test_list(self):
		self.check_changelist()

	def test_add(self):
		self.check_add(self.DEFAULT_ADD_DATA)

	def test_change(self):
		user = User.objects.get_or_create(**self.DEFAULT_DATA)[0]
		user.save()
		data = self.DEFAULT_DATA.copy()
		data['username'] = 'abc'
		user = self.check_change(user.pk, data)['instance']
		self.assertEqual(user.username, data['username'])

	def test_admin_actions(self):
		user = User.objects.get_or_create(**self.DEFAULT_DATA)[0]
		user.is_active = True
		user.save()
		user = self.check_action(user.pk, 'set_inactive', self.DEFAULT_DATA)['instance']
		self.assertFalse(user.is_active)
		user = self.check_action(user.pk, 'set_active', self.DEFAULT_DATA)['instance']
		self.assertTrue(user.is_active)

	def test_delete(self):
		user = User.objects.get_or_create(**self.DEFAULT_DATA)[0]
		user.save()
		user = User.objects.get(pk=user.pk)
		self.check_delete(user.pk)
