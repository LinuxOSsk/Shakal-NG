# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.timezone import now, timedelta

from article.models import Category, Article


class ArticleModelTest(TestCase):
	def setUp(self):
		category = Category()
		category.name = "Category"
		category.slug = "category"
		category.icon = "/icon.png"
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

		all_articles = Article._default_manager.all()
		self.assertEqual(len(all_articles), 1)

	def test_article_in_future(self):
		article = self.create_article_instance()
		article.pub_time = now() + timedelta(1)
		article.full_clean()
		article.save()

		articles = Article.objects.all()
		self.assertEqual(len(articles), 0)

		all_articles = Article._default_manager.all()
		self.assertEqual(len(all_articles), 1)

	def test_not_allowed_integer_slugs(self):
		article = self.create_article_instance()
		article.slug = 1
		with self.assertRaises(ValidationError):
			article.full_clean()

	def create_article_instance(self):
		article = Article()
		article.title = "title"
		article.slug = "slug"
		article.category = Category.objects.all()[0]
		article.perex = "perex"
		article.annotation = "annotation"
		article.authors_name = "author"
		article.published = True
		article.top = False
		article.pub_time = now()
		article.updated = now()
		article.content = "content"
		return article
