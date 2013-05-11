# -*- coding: utf-8 -*-
from django.test import TestCase
from rich_editor.parser import HtmlParser


class ParserTest(TestCase):
	def setUp(self):
		self.parser = HtmlParser()

	def test_valid_html(self):
		code = "<strong>Test</strong>\n<pre>\nTadaaa\n</pre>\n<p>Text</p>"
		self.parser.parse(code)
		self.assertEquals(self.parser.get_output(), code)

	def test_opened_tag(self):
		code = """<p>Test"""
		self.parser.parse(code)
		self.assertEquals(self.parser.get_output(), code + "</p>")

	def test_opened_nested_tag(self):
		code = """<p><strong>Test</p>"""
		self.parser.parse(code)
		self.assertEquals(self.parser.get_output(), code[:-4] + "</strong></p>")

	def test_unknown_tag(self):
		code = """<xxx>Test</xxx>"""
		self.parser.parse(code)
		self.assertEquals(self.parser.get_output(), code.replace('<', '&lt;').replace('>', '&gt;'))

	def test_attribute(self):
		code = """<p><a href="#test">Test</a></p>"""
		self.parser.parse(code)
		self.assertEquals(self.parser.get_output(), code)

	def test_missing_attribute(self):
		code = """<p><a>Test</a></p>"""
		self.parser.parse(code)
		self.assertEquals(self.parser.get_output(), """<p><a href="#">Test</a></p>""")

	def test_empty_tag(self):
		code = """<p></p>"""
		self.parser.parse(code)
		self.assertEquals(self.parser.get_output(), """<p>&nbsp;</p>""")

	def test_malicious_href(self):
		code = """<p><a href="javascript:alert('XSS')">Test</a></p>"""
		self.parser.parse(code)
		self.assertEquals(self.parser.get_output(), """<p><a href="#">Test</a></p>""")
