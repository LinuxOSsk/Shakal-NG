# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import User
from django_sample_generator import GeneratorRegister, ModelGenerator, samples
from django.utils import timezone
from django.conf import settings


class SuperuserGenerator(ModelGenerator):
	def __init__(self, *args, **kwargs):
		self.users = []

		last_login = timezone.now()

		admin = User()
		admin.email = "superadmin@admin.admin"
		admin.username = "admin"
		admin.is_staff = True
		admin.is_superuser = True
		admin.set_password("demo")
		admin.last_login = last_login
		self.users.append(admin)

		demo = User()
		demo.email = "demo@demo.demo"
		demo.username = "demo"
		demo.is_staff = False
		demo.is_superuser = False
		demo.set_password("demo")
		demo.last_login = last_login
		self.users.append(demo)

		kwargs["count"] = len(self.users)
		super(SuperuserGenerator, self).__init__(*args, **kwargs)

	def __iter__(self):
		return iter(self.users)


class UserGenerator(ModelGenerator):
	email = samples.EmailSample()

	def get_object(self):
		obj = super(UserGenerator, self).get_object()
		obj.username = obj.email.replace('@', '_').replace('.', '_')
		obj.is_staff = False
		obj.is_superuser = False
		obj.last_login = timezone.now()
		return obj


register = GeneratorRegister()
register.register(SuperuserGenerator(User))
register.register(UserGenerator(User, settings.INITIAL_DATA_COUNT['user'] - 2))
