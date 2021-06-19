# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Statistics, Rating
from article.models import Article, Category


User = get_user_model()


class RatingTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.category = Category.objects.create(name='ccategory', slug='category')
		cls.articles = [
			Article.objects.create(title='test %d' % i, slug='test-%d' % i, category=cls.category)
			for i in range(1, 3)
		]
		cls.users = [
			User.objects.create_user(username='test%d' % i, email='test%d@test.tld' % i)
			for i in range(1, 3)
		]

	def add_rating(self, value=None, marked_solution=None, marked_flag=None, user=1, article=1):
		user = self.users[user - 1]
		obj = self.articles[article - 1]
		Rating.objects.rate(
			instance=obj,
			user=user,
			value=value,
			marked_solution=marked_solution,
			marked_flag=marked_flag
		)

	def test_add_rating(self):
		self.add_rating(value=1)
		self.assertEquals(Rating.objects.count(), 1)

	def test_replace_rating(self):
		self.add_rating(value=1)
		self.add_rating(value=-1)
		self.assertEquals(Rating.objects.count(), 1)
		self.assertEquals(Rating.objects.first().value, -1)

	def test_rate_from_multiple_users(self):
		self.add_rating(value=1, user=1)
		self.add_rating(value=1, user=2)
		self.assertEquals(Rating.objects.count(), 2)

	def test_rate_multiple_objects(self):
		self.add_rating(value=1, article=1, user=1)
		self.add_rating(value=1, article=2, user=1)
		self.assertEquals(Rating.objects.count(), 2)

	def test_statistics_rating_count(self):
		self.add_rating(value=1, user=1)
		self.add_rating(value=1, user=2)
		self.assertEquals(Rating.objects.count(), 2)
		self.assertEquals(Statistics.objects.first().rating_count, 2)

	def test_statistics_empty_value(self):
		self.add_rating(value=1, user=1)
		self.add_rating(value=None, user=2)
		self.assertEquals(Rating.objects.count(), 2)
		self.assertEquals(Statistics.objects.first().rating_count, 1)

	def test_statistics_rating_total(self):
		self.add_rating(value=1, user=1)
		self.add_rating(value=2, user=2)
		self.assertEquals(Statistics.objects.first().rating_total, 3)

	def test_statistics_rating_total_with_empty(self):
		self.add_rating(value=None, user=1)
		self.add_rating(value=2, user=2)
		self.assertEquals(Statistics.objects.first().rating_total, 2)

	def test_statistics_mark_solution(self):
		self.add_rating(marked_solution=True, user=1)
		self.add_rating(marked_solution=False, user=2)
		self.assertEquals(Rating.objects.count(), 2)
		self.assertEquals(Statistics.objects.first().solution_count, 1)

	def test_statistics_mark_flag(self):
		self.add_rating(marked_flag=Rating.FLAG_SPAM, user=1)
		self.add_rating(marked_flag=Rating.FLAG_NONE, user=2)
		self.assertEquals(Rating.objects.count(), 2)
		self.assertEquals(Statistics.objects.first().flag_count, 1)
