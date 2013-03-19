# -*- coding: utf-8 -*-
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from common import admin_login
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class ArticleTest(LiveServerTestCase):
	fixtures = ['accounts_user.json']

	def setUp(self):
		self.browser = webdriver.Firefox()
		self.browser.implicitly_wait(5)

	def tearDown(self):
		self.browser.quit()

	def test_add(self):
		admin_login(self)
		self.browser.get(self.live_server_url + reverse('admin:article_category_add'))

		name_field = self.browser.find_element_by_name('name')
		name_field.send_keys('Category')

		icon_field = self.browser.find_element_by_name('icon')
		icon_field.send_keys('category.png')
		icon_field.send_keys(Keys.RETURN)

		self.browser.get(self.live_server_url + reverse('admin:article_article_add'))

		category_field = self.browser.find_element_by_name('category')
		for option in category_field.find_elements_by_tag_name('option'):
			if option.text == 'Category':
				option.click()

		article_form = self.browser.find_element_by_id('article_form')

		published_field = article_form.find_element_by_name('published')
		published_field.click()

		title_field = article_form.find_element_by_name('title')
		title_field.send_keys('Article title')

		perex_field = article_form.find_element_by_name('perex')
		perex_field.send_keys('perex')

		annotation_field = article_form.find_element_by_name('annotation')
		annotation_field.send_keys('annotation')

		content_field = article_form.find_element_by_name('content')
		content_field.send_keys('Content')

		authors_name_field = article_form.find_element_by_name('authors_name')
		authors_name_field.send_keys('author')
		authors_name_field.send_keys(Keys.RETURN)

		self.browser.get(self.live_server_url + reverse('home'))

		body = self.browser.find_element_by_tag_name('body')
		self.assertIn("Article title", body.text)
