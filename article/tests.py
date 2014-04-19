# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.timezone import now, timedelta
from common_utils.tests_common import AdminSiteTestCase, fts_test

from .models import Category, Article


class ArticleModelTest(TestCase):
	def setUp(self):
		category = Category()
		category.name = 'Category'
		category.slug = 'category'
		category.save()

		all_categories = Category.objects.all()
		self.assertEqual(len(all_categories), 1)

		category_from_database = all_categories[0]
		self.assertEqual(category_from_database, category)

	def test_create_article(self):
		article = self.create_article_instance()
		article.full_clean()
		article.save()

		all_articles = Article.objects.all()
		self.assertEqual(len(all_articles), 1)

		article_from_database = all_articles[0]
		self.assertEqual(article_from_database, article)

	def test_article_private(self):
		article = self.create_article_instance()
		article.published = False
		article.full_clean()
		article.save()

		articles = Article.objects.all()
		self.assertEqual(len(articles), 0)

	def test_article_in_future(self):
		article = self.create_article_instance()
		article.pub_time = now() + timedelta(1)
		article.full_clean()
		article.save()

		articles = Article.objects.all()
		self.assertEqual(len(articles), 0)

	def test_not_allowed_integer_slugs(self):
		article = self.create_article_instance()
		article.slug = 1
		with self.assertRaises(ValidationError):
			article.full_clean()

	def test_hit_count(self):
		article = self.create_article_instance()
		article.save()

		self.assertEqual(article.hit_count, 0) #pylint: disable=E1101
		article.hit() #pylint: disable=E1102
		self.assertEqual(article.hit_count, 1) #pylint: disable=E1101

	def create_article_instance(self):
		article = Article()
		article.title = 'title'
		article.slug = 'slug'
		article.category = Category.objects.all()[0]
		article.perex = 'perex'
		article.annotation = 'annotation'
		article.authors_name = 'author'
		article.published = True
		article.top = False
		article.pub_time = now()
		article.updated = now()
		article.content = 'content'
		return article


@fts_test
class CategoryAdminTest(AdminSiteTestCase):
	model = 'category'

	DEFAULT_DATA = {
		'name': 'Category',
		'slug': 'category',
		'description': 'Description',
	}

	def setUp(self):
		self.login('admin', 'P4ssw0rd')

	@staticmethod
	def create_category():
		c = Category(**CategoryAdminTest.DEFAULT_DATA)
		c.save()
		return c

	def test_list(self):
		self.create_category()
		self.check_changelist()

	def test_add(self):
		self.check_add(self.DEFAULT_DATA)

	def test_change(self):
		category = self.create_category()
		new_data = self.DEFAULT_DATA.copy()
		new_data['name'] = 'New category'
		category = self.check_change(category.pk, new_data)['instance']
		self.assertEqual(category.name, 'New category')

	def test_delete(self):
		category = self.create_category()
		self.check_delete(category.pk)


@fts_test
class ArticleAdminTest(AdminSiteTestCase):
	model = 'article'

	DEFAULT_DATA = {
		'title': 'Article',
		'slug': 'article',
		'perex': 'perex',
		'annotation': 'annotation',
		'content': 'content',
		'authors_name': 'author',
		'pub_time': now(),
		'published': '1',
		'top': '',
	}

	def setUp(self):
		self.user = self.login('admin', 'P4ssw0rd')
		self.category = Category(name='Category', slug='new-category', description='Description')
		self.category.save()

	@staticmethod
	def create_article(category, author):
		a = Article(**ArticleAdminTest.DEFAULT_DATA)
		a.author = author
		a.category = category
		a.save()
		return a

	def test_list(self):
		self.create_article(CategoryAdminTest.create_category(), self.user)
		self.check_changelist()

	def test_add(self):
		category = CategoryAdminTest.create_category()
		data = self.DEFAULT_DATA.copy()
		del data['pub_time']
		data['category'] = category.pk
		data['author'] = self.user.pk
		data['pub_time_0'] = '2000-01-01'
		data['pub_time_1'] = '00:00:00'
		self.check_add(data)

	def test_change(self):
		article = self.create_article(CategoryAdminTest.create_category(), self.user)
		article = self.check_change(article.pk, {'title': 'New title'})['instance']
		self.assertEqual(article.title, 'New title')

	def test_delete(self):
		article = self.create_article(CategoryAdminTest.create_category(), self.user)
		self.check_delete(article.pk)
