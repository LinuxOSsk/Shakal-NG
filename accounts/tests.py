# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import User


class UserModelTest(TestCase):
	def test_creating_new_user(self):
		user = User()
		user.username = "test"
		user.email = "test@test.com"
		user.set_password("test")
		user.full_clean()
		user.save()

		all_users = User.objects.all()
		self.assertEqual(len(all_users), 1)

		user_from_database = all_users[0]
		self.assertEquals(user_from_database, user)

	def test_duplicate_email_check(self):
		user = User()
		user.username = "test"
		user.email = "test@test.com"
		user.set_password("test")
		user.full_clean()
		user.save()

		with self.assertRaises(ValidationError):
			user2 = User()
			user2.username = "test2"
			user2.email = "test@test.com"
			user2.set_password("test")
			user2.full_clean()
			user2.save()
