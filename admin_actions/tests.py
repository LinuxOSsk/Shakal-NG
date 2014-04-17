# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http.response import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory

from .views import AdminActionsMixin


class FakeAdmin(object):
	def get_object(self, *_):
		return None

	def change_view(self, *_):
		return HttpResponse("change view")


class TestAdmin(AdminActionsMixin, FakeAdmin):
	changelist_actions = (('return_response', "Return response"), ("return_change_view", "Return change view"))

	def return_response(self, **_):
		return HttpResponse("direct response")

	def return_change_view(self, **_):
		return None


class AdminActionsMixinTest(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.admin = TestAdmin()

	def test_return_response(self):
		request = self.factory.post("/", {'_return_response': 1})
		response = self.admin.change_view(request, "1")
		self.assertEqual(response.content, "direct response")

	def test_return_change_view(self):
		request = self.factory.post("/", {'_return_change_view': 1})
		response = self.admin.change_view(request, "1")
		self.assertEqual(response.content, "change view")
