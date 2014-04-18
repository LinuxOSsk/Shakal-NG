# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.conf import settings
from django.forms import Form
from django.test.client import RequestFactory
from django.utils import unittest

from antispam.fields import AntispamInput, AntispamField
from antispam.forms import AntispamFormMixin


class AntispamTestCase(unittest.TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.old_captcha_disable = settings.CAPTCHA_DISABLE
		settings.CAPTCHA_DISABLE = False

	def tearDown(self):
		settings.CAPTCHA_DISABLE = self.old_captcha_disable

	def test_input(self):
		test_input = AntispamInput(attrs = {"question": "Question", "answer": "Answer"})
		input_code = test_input.render("captcha", "0")
		self.assertIn("Question", input_code)
		self.assertNotIn("Answer", input_code)

	def test_field(self):
		test_field = AntispamField()
		test_field.widget.attrs['question'] = '1 + 1'
		test_field.widget.attrs['answer'] = '2'
		# chybná odpoveď
		with self.assertRaises(ValidationError):
			test_field.clean('3')
		# v poiriadku
		test_field.clean('2')

	def test_antispam_form(self):
		class AntispamForm(AntispamFormMixin, Form):
			pass
		test_form = AntispamForm()
		get_request = self.factory.get('/')
		get_request.session = {}
		test_form.process_antispam(get_request)
		# nastavenie session
		self.assertIn("antispam", get_request.session)

		post_request = self.factory.post('/')
		post_request.session = get_request.session

		# OK
		bound_form = AntispamForm({'captcha': test_form.fields['captcha'].widget.attrs['answer']}, request=post_request)
		self.assertTrue(bound_form.is_valid())

		# Chyba
		bound_form = AntispamForm({'captcha': test_form.fields['captcha'].widget.attrs['answer'] + '0'}, request=post_request)
		self.assertFalse(bound_form.is_valid())
