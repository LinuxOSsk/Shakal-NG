# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from common import admin_login


class ArticleTest(LiveServerTestCase):
	fixtures = ['accounts_user.json']

	def setUp(self):
		self.OLD_TEMPLATES = settings.TEMPLATES
		settings.TEMPLATES = (('desktop', ('default',),),)
		self.browser = webdriver.Firefox()
		self.browser.implicitly_wait(5)

	def tearDown(self):
		self.browser.quit()
		settings.TEMPLATES = self.OLD_TEMPLATES

	def test_add(self):
		admin_login(self)
		self.browser.get(self.live_server_url + reverse('admin:article_category_add'))

		description_field = self.browser.find_element_by_name('description')
		description_field.send_keys('Description')

		name_field = self.browser.find_element_by_name('name')
		name_field.send_keys('Category')
		name_field.send_keys(Keys.RETURN)

		self.browser.get(self.live_server_url + reverse('admin:article_article_add'))

		article_form = self.browser.find_element_by_id('article_form')

		category_field = article_form.find_element_by_name('category')
		for option in category_field.find_elements_by_tag_name('option'):
			if option.text == 'Category':
				option.click()

		title_field = article_form.find_element_by_name('title')
		title_field.click()
		title_field.send_keys('Article title')

		import time
		time.sleep(200)

		perex_field = article_form.find_element_by_name('perex')
		perex_field.send_keys('perex')

		annotation_field = article_form.find_element_by_name('annotation')
		annotation_field.send_keys('annotation')

		content_field = article_form.find_element_by_name('content')
		content_field.send_keys('Content')

		published_field = article_form.find_element_by_name('published')
		published_field.click()

		pub_date_field = article_form.find_element_by_name('pub_time_0')
		pub_date_field.clear()
		pub_date_field.send_keys("1970-01-01")

		pub_time_field = article_form.find_element_by_name('pub_time_1')
		pub_time_field.clear()
		pub_time_field.send_keys("0:00:00")

		authors_name_field = article_form.find_element_by_name('authors_name')
		authors_name_field.send_keys('author')
		authors_name_field.send_keys(Keys.RETURN)

		self.browser.get(self.live_server_url + reverse('home'))

		body = self.browser.find_element_by_tag_name('body')
		self.assertIn("Article title", body.text)
