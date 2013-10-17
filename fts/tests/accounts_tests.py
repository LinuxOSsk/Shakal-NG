# -*- coding: utf-8 -*-
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from .common import admin_login, logout, login
from accounts.models import User


class AccountsTest(LiveServerTestCase):
	fixtures = ['accounts_user.json']

	def setUp(self):
		self.browser = webdriver.Firefox()
		self.browser.implicitly_wait(30)

	def tearDown(self):
		self.browser.quit()

	def fill_password(self):
		self.browser.find_element_by_id("id_password1").clear()
		self.browser.find_element_by_id("id_password1").send_keys("P4ssword")
		self.browser.find_element_by_id("id_password2").clear()
		self.browser.find_element_by_id("id_password2").send_keys("P4ssword")

	def get_mail_link(self):
		self.assertEqual(len(mail.outbox), 1)
		message_body = str(mail.outbox[0].message())
		import re
		link_match = re.search(r'http(?s)://[-\w_:.\/@]*', message_body)
		self.assertNotEqual(link_match, None)
		return link_match.group(0)

	def is_element_present(self, how, what):
		try:
			self.browser.find_element(by=how, value=what)
		except NoSuchElementException:
			return False
		return True

	def test_crate_account_via_admin_site(self):
		admin_login(self)
		self.browser.get(self.live_server_url + reverse('admin:accounts_user_changelist'))
		self.browser.find_element_by_link_text("Users").click()
		self.browser.find_element_by_css_selector("i.icon-plus-sign.icon-white").click()
		self.browser.find_element_by_id("id_username").clear()
		self.browser.find_element_by_id("id_username").send_keys("new_user")
		self.fill_password()
		self.browser.find_element_by_name("_save").click()
		self.assertTrue(self.is_element_present(By.CSS_SELECTOR, "div.alert.alert-info"))

	def test_duplicate_email_check(self):
		self.browser.get(self.live_server_url + reverse('registration_register'))
		self.browser.find_element_by_id("id_username").clear()
		self.browser.find_element_by_id("id_username").send_keys("new_user2")
		self.browser.find_element_by_id("id_email").clear()
		self.browser.find_element_by_id("id_email").send_keys("admin@example.com")
		self.fill_password()
		self.browser.find_element_by_css_selector("button.btn").click()
		self.assertEqual("This email address is already in use. Please supply a different email address.", self.browser.find_element_by_css_selector(".errorlist>*").text)

	def test_create_user(self):
		self.browser.get(self.live_server_url + reverse('registration_register'))
		self.browser.find_element_by_id("id_username").clear()
		self.browser.find_element_by_id("id_username").send_keys("new_user2")
		self.browser.find_element_by_id("id_email").clear()
		self.browser.find_element_by_id("id_email").send_keys("user2@example.com")
		self.fill_password()
		self.browser.find_element_by_css_selector("button.btn").click()
		self.assertEqual("Registration complete!", self.browser.find_element_by_css_selector("h1").text)

		self.browser.get(self.get_mail_link())
		self.assertEqual("Your account is now active!", self.browser.find_element_by_css_selector("h1").text)

	def test_login_user(self):
		self.browser.get(self.live_server_url + reverse('auth_login'))
		self.browser.find_element_by_id("id_username").clear()
		self.browser.find_element_by_id("id_username").send_keys("user")
		self.browser.find_element_by_id("id_password").clear()
		self.browser.find_element_by_id("id_password").send_keys("pass")
		self.browser.find_element_by_css_selector("button.btn").click()
		self.assertEqual("- User profile", self.browser.title)
		logout(self)

	def test_profile_edit(self):
		login(self, "user", "pass")
		self.profile_check_bad_password()
		self.profile_change_data()
		self.profile_change_email()
		self.profile_change_password()

	def profile_check_bad_password(self):
		self.browser.get(self.live_server_url + reverse('auth_my_profile_edit'))
		self.browser.find_element_by_id("id_current_password").clear()
		self.browser.find_element_by_id("id_current_password").send_keys("bad")
		self.browser.find_element_by_css_selector("button.btn").click()
		self.assertEqual("Please enter the correct password.", self.browser.find_element_by_css_selector("ul.errorlist > li").text)

	def profile_change_data(self):
		self.browser.get(self.live_server_url + reverse('auth_my_profile_edit'))
		self.browser.find_element_by_id("id_current_password").clear()
		self.browser.find_element_by_id("id_current_password").send_keys("pass")
		self.browser.find_element_by_id("id_first_name").clear()
		self.browser.find_element_by_id("id_first_name").send_keys("Joe")
		self.browser.find_element_by_id("id_last_name").clear()
		self.browser.find_element_by_id("id_last_name").send_keys("Smith")
		self.browser.find_element_by_css_selector("button.btn").click()
		self.assertTrue(self.is_element_present(By.CSS_SELECTOR, "dd.fn"))

	def profile_change_email(self):
		self.browser.get(self.live_server_url + reverse('auth_my_profile_edit'))
		self.browser.find_element_by_link_text("Change e-mail").click()
		self.browser.find_element_by_id("id_email").clear()
		self.browser.find_element_by_id("id_email").send_keys("admin@example.com")
		self.browser.find_element_by_id("id_current_password").clear()
		self.browser.find_element_by_id("id_current_password").send_keys("pass")
		self.browser.find_element_by_css_selector("button.btn").click()
		self.assertEqual("User with this Email address already exists.", self.browser.find_element_by_css_selector("li").text)
		self.browser.find_element_by_id("id_current_password").clear()
		self.browser.find_element_by_id("id_current_password").send_keys("pass")
		self.browser.find_element_by_id("id_email").clear()
		self.browser.find_element_by_id("id_email").send_keys("newmail@example.com")
		self.browser.find_element_by_css_selector("button.btn").click()
		self.assertEqual("E-mail change request sent", self.browser.find_element_by_css_selector("h1").text)
		self.browser.get(self.get_mail_link())
		self.assertEqual("E-mail change complete", self.browser.find_element_by_css_selector("h1").text)
		User.objects.filter(email='newmail@example.com').update(email='user@example.com')

	def profile_change_password(self):
		self.browser.get(self.live_server_url + reverse('auth_my_profile_edit'))
		self.browser.find_element_by_link_text("Change password").click()
		self.browser.find_element_by_id("id_old_password").clear()
		self.browser.find_element_by_id("id_old_password").send_keys("bad")
		self.browser.find_element_by_id("id_new_password1").clear()
		self.browser.find_element_by_id("id_new_password1").send_keys("newPass")
		self.browser.find_element_by_id("id_new_password2").clear()
		self.browser.find_element_by_id("id_new_password2").send_keys("newPass")
		self.browser.find_element_by_css_selector("button.btn").click()
		self.assertEqual("Your old password was entered incorrectly. Please enter it again.", self.browser.find_element_by_css_selector("li").text)
		self.browser.find_element_by_id("id_old_password").clear()
		self.browser.find_element_by_id("id_old_password").send_keys("pass")
		self.browser.find_element_by_id("id_new_password1").clear()
		self.browser.find_element_by_id("id_new_password1").send_keys("bad")
		self.browser.find_element_by_id("id_new_password2").clear()
		self.browser.find_element_by_id("id_new_password2").send_keys("newPass")
		self.browser.find_element_by_css_selector("button.btn").click()
		self.assertEqual("The two password fields didn't match.", self.browser.find_element_by_css_selector("li").text)
		self.browser.find_element_by_id("id_old_password").clear()
		self.browser.find_element_by_id("id_old_password").send_keys("pass")
		self.browser.find_element_by_id("id_new_password1").clear()
		self.browser.find_element_by_id("id_new_password1").send_keys("newPass")
		self.browser.find_element_by_id("id_new_password2").clear()
		self.browser.find_element_by_id("id_new_password2").send_keys("newPass")
		self.browser.find_element_by_css_selector("button.btn").click()
		self.assertEqual("Password change successful", self.browser.find_element_by_css_selector("h1").text)

	def test_password_reset(self):
		self.browser.get(self.live_server_url + reverse('auth_password_reset'))
		self.browser.find_element_by_id("id_email").clear()
		self.browser.find_element_by_id("id_email").send_keys("user@example.com")
		self.browser.find_element_by_css_selector("input[type=\"submit\"]").click()
		self.browser.get(self.get_mail_link())
		self.browser.find_element_by_id("id_new_password1").clear()
		self.browser.find_element_by_id("id_new_password1").send_keys("pass")
		self.browser.find_element_by_id("id_new_password2").clear()
		self.browser.find_element_by_id("id_new_password2").send_keys("pass")
		self.browser.find_element_by_css_selector("button.btn").click()
		self.assertEqual("Password reset complete", self.browser.find_element_by_css_selector("h1").text)
