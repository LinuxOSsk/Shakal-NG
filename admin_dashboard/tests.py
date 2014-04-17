# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.test.client import RequestFactory
from .views import stats
from accounts.models import User
import json


class StatsTest(TestCase):
	fixtures = ['users.json']

	def setUp(self):
		self.factory = RequestFactory()
		self.user = User.objects.get(pk=1)

	def test_list(self):
		request = self.factory.get("/")
		request.user = self.user
		json.loads(stats(request).content)

	def test_stat(self):
		request = self.factory.get("/?type=comments&interval=days&start_day=-30&end_day=0&aggregate=1")
		request.user = self.user
		json.loads(stats(request).content)

		request = self.factory.get("/?type=comments&interval=days&start_day=-30&end_day=0&aggregate=1&format=csv")
		request.user = self.user
		stats(request)

		with self.assertRaises(ValueError):
			request = self.factory.get("/?type=comments&interval=days&start_day=-30&end_day=-31&aggregate=1")
			request.user = self.user
			stats(request)

		with self.assertRaises(ValueError):
			request = self.factory.get("/?type=comments&interval=days&start_day=-30&end_day=0&aggregate=1000")
			request.user = self.user
			stats(request)

		with self.assertRaises(ValueError):
			request = self.factory.get("/?type=comments&interval=xxx&start_day=-30&end_day=0&aggregate=1")
			request.user = self.user
			stats(request)

		with self.assertRaises(ValueError):
			request = self.factory.get("/?type=comments&interval=days&start_day=-10000&end_day=0&aggregate=1")
			request.user = self.user
			stats(request)
