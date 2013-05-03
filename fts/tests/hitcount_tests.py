# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase

from selenium import webdriver
from article.models import Article, Category


class HitCountTest(LiveServerTestCase):
	def setUp(self):
		self.OLD_TEMPLATES = settings.TEMPLATES
		settings.TEMPLATES = (('desktop', ('default',),),)
		category = Category(name = "t", slug = "t")
		category.save()
		article = Article()
		article.category = category
		article.published = True
		article.title = "Article title"
		article.slug = "article"
		article.save()
		self.article = article
		self.browser = webdriver.Firefox()
		self.browser.implicitly_wait(5)

	def tearDown(self):
		self.browser.quit()
		settings.TEMPLATES = self.OLD_TEMPLATES

	def test_hit(self):
		self.browser.get(self.live_server_url + reverse('home'))

		body = self.browser.find_element_by_tag_name('body')
		self.assertIn("0x", body.text)

		article_link = self.browser.find_element_by_link_text("Article title")
		article_link.click()
		body = self.browser.find_element_by_tag_name('body')
		self.assertIn("Article title", body.text)

		self.browser.get(self.live_server_url + reverse('home'))
		body = self.browser.find_element_by_tag_name('body')
		self.assertIn("1x", body.text)
