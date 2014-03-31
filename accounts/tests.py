# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.core import mail
from django.test import TestCase
import os

from .admin_forms import UserCreationForm
from .forms import ProfileEditForm
from .models import User, UserRating, RATING_WEIGHTS
from .registration_backend.forms import UserRegistrationForm
from .templatetags.avatar import avatar_for_user
from common_utils.tests_common import AdminSiteTestCase, ProcessFormTestMixin, fts_test


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


class UserModelTest(TestCase):
	fixtures = ['users.json']

	def test_duplicate_mail(self):
		user = User(username="user2", email="admin@example.com")
		with self.assertRaises(ValidationError):
			user.clean_fields()

	def test_permalink(self):
		user = User.objects.get(username="user")
		self.assertNotEqual(user.get_absolute_url(), "/")

	def test_encrypt_password(self):
		with self.settings(ENCRYPT_KEY=os.path.join(os.path.dirname(__file__), "test.der")):
			user = User.objects.get(username="user")
			user.set_password("test")
			self.assertIsNotNone(user.encrypted_password)


class UserRatingModelTest(TestCase):
	def test_rating(self):
		from news.models import News

		user = User(username="unique", email="unique@example.com")
		user.save()

		news = News(title="Test", slug="test", approved=True, author=user)
		news.save()

		rating = UserRating.objects.get(user=user)
		self.assertEqual(rating.rating, RATING_WEIGHTS['news'])
		self.assertEqual(str(rating), '2')

		news.approved = False
		news.save()

		rating = UserRating.objects.get(user=user)
		self.assertEqual(rating.rating, 0)

		news.delete()
		rating = UserRating.objects.get(user=user)
		self.assertEqual(rating.rating, 0)


@fts_test
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
		'first_name': 'firstname',
		'last_name': 'lastname',
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


@fts_test
class UserRegistrationTest(ProcessFormTestMixin, TestCase):
	def test_register(self):
		with self.settings(CAPTCHA_DISABLE=True):
			form = self.extract_form("registration_register")
			user_data = {'username': 'unique', 'password1': 'P4ssw0rd', 'password2': 'P4ssw0rd', 'email': 'unique@example.com'}
			form_data = self.fill_form(form, user_data)
			response = self.send_form_data("registration_register", form_data)
			self.assertEqual(len(mail.outbox), 1)


class AvatarTest(TestCase):
	def test_for_user(self):
		user = User(email="uňicoďe@example.com")
		self.assertNotEqual(avatar_for_user(user), "")
