# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Sum
from django.test import TestCase
from .models import Statistics, Rating
from article.models import Article, Category
from django.contrib.auth import get_user_model


User = get_user_model()


class RatingTest(TestCase):
	def setUp(self):
		self.category = Category.objects.create(name='ccategory', slug='category')
		self.test_obj = Article.objects.create(title='test', slug='test', category=self.category)
		self.test_obj2 = Article.objects.create(title='test2', slug='test2', category=self.category)
		self.user1 = User.objects.create_user(username='test', email='test@test.tld')
		self.user2 = User.objects.create_user(username='test2', email='test2@test.tld')

	def test_add_rating(self):
		Rating.objects.rate(instance=self.test_obj, value=1, user=self.user1)
		Rating.objects.rate(instance=self.test_obj2, value=1, user=self.user2)
		self.assertEquals(Rating.objects.count(), 2)

	def test_unique_rating(self):
		Rating.objects.rate(instance=self.test_obj, value=1, user=self.user1)
		self.assertEquals(Rating.objects.count(), 1)
		Rating.objects.rate(instance=self.test_obj, value=-1, user=self.user1)
		self.assertEquals(Rating.objects.count(), 1)

		Rating.objects.rate(instance=self.test_obj, value=1, user=self.user2)
		self.assertEquals(Rating.objects.count(), 2)

		Rating.objects.rate(instance=self.test_obj2, value=1, user=self.user1)
		self.assertEquals(Rating.objects.count(), 3)

	def test_change_rating(self):
		Rating.objects.rate(instance=self.test_obj, value=1, user=self.user1)
		Rating.objects.rate(instance=self.test_obj, value=-1, user=self.user1)
		self.assertEquals(Rating.objects.first().value, -1)

	def test_statistics(self):
		Rating.objects.rate(instance=self.test_obj, value=1, user=self.user1)
		Rating.objects.all().delete()
		Statistics.objects.all().refresh_statistics()
		stat = Statistics.objects.first()
		self.assertEquals(stat.rating_total, 0)
		self.assertEquals(stat.rating_count, 0)
		self.assertEquals(stat.solution_count, 0)
		Rating.objects.rate(instance=self.test_obj, value=1, user=self.user1)
		Rating.objects.rate(instance=self.test_obj, value=-1, marked_solution=True, user=self.user2)
		stat.refresh_from_db()
		self.assertEquals(stat.rating_total, 0)
		self.assertEquals(stat.rating_count, 2)
		self.assertEquals(stat.solution_count, 1)
		Rating.objects.rate(instance=self.test_obj, value=False, marked_solution=False, user=self.user2)
		stat.refresh_from_db()
		self.assertEquals(stat.rating_total, 1)
		self.assertEquals(stat.rating_count, 1)
		self.assertEquals(stat.solution_count, 0)
