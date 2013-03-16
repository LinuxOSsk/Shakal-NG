# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class AccountsTest(LiveServerTestCase):
	fixtures = ['accounts_user.json']

	def setUp(self):
		self.browser = webdriver.Firefox()
		self.browser.implicitly_wait(3)

	def tearDown(self):
		self.browser.quit()

	def test_create_account_via_admin_site(self):
		self.browser.get(self.live_server_url + reverse('admin:index'))

		username_field = self.browser.find_element_by_name('username')
		username_field.send_keys('admin')

		password_field = self.browser.find_element_by_name('password')
		password_field.send_keys('pass')
		password_field.send_keys(Keys.RETURN)

		self.browser.get(self.live_server_url + reverse('admin:accounts_user_changelist'))
		user_rows = self.browser.find_elements_by_css_selector('#result_list tbody tr')
		self.assertEquals(len(user_rows), 1)

		self.browser.get(self.live_server_url + reverse('admin:accounts_user_add'))
		create_username_field = self.browser.find_element_by_name('username')
		create_username_field.send_keys('user2')

		create_password_field1 = self.browser.find_element_by_name('password1')
		create_password_field1.send_keys('password')

		create_password_field2 = self.browser.find_element_by_name('password2')
		create_password_field2.send_keys('password')
		create_password_field2.send_keys(Keys.RETURN)

		info_rows = self.browser.find_elements_by_css_selector('.messagelist .info')
		self.assertEquals(len(info_rows), 1)
