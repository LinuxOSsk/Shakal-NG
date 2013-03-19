# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext
from selenium.webdriver.common.keys import Keys

def admin_login(self):
	self.browser.get(self.live_server_url + reverse('admin:index'))

	username_field = self.browser.find_element_by_name('username')
	username_field.send_keys('admin')

	password_field = self.browser.find_element_by_name('password')
	password_field.send_keys('pass')
	password_field.send_keys(Keys.RETURN)


def logout(self):
	self.browser.get(self.live_server_url + reverse('auth_logout'))
	body = self.browser.find_element_by_tag_name('body')
	self.assertIn(ugettext("Logged out"), body.text)
