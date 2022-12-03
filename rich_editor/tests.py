# -*- coding: utf-8 -*-
from django.test import TestCase
from rich_editor.parser import HtmlParser
from rich_editor.syntax import highlight_pre_blocks
from rich_editor import get_parser


class ParserTest(TestCase):
	def setUp(self):
		self.parser = HtmlParser()
		self.parser.auto_paragraphs = True
		self.parser.add_nofollow = False

	def test_auto_paragraph(self):
		code = """Test"""
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), "<p>" + code + "</p>")

	def test_valid_html(self):
		code = "<p><strong>Test</strong></p>\n<pre>Tadaaa\n\n</pre><p>Text</p>"
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), "<p><strong>Test</strong></p>\n<pre>Tadaaa\n\n</pre><p>Text</p>")

	def test_opened_tag(self):
		code = """<p>Test"""
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), code + "</p>")

	def test_opened_nested_tag(self):
		code = """<p><strong>Test</p>"""
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), code[:-4] + "</strong></p>")

	def test_unknown_tag(self):
		code = """<xxx>Test</xxx>"""
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), '<p>' + code.replace('<', '&lt;').replace('>', '&gt;') + '</p>')

	def test_attribute(self):
		code = """<p><a href="#test">Test</a></p>"""
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), code)

	def test_missing_attribute(self):
		code = """<p><a>Test</a></p>"""
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), """<p><a href="#">Test</a></p>""")

	def test_malicious_href(self):
		code = """<p><a href="javascript:alert('XSS')">Test</a></p>"""
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), """<p><a href="#">Test</a></p>""")

	def test_signature_nofollow(self):
		code = """<a href="http://www.linuxos.sk">Test</a>"""
		parser = get_parser('signature')
		parser.parse(code)
		self.assertEqual(parser.get_output(), """<a href="http://www.linuxos.sk" rel="nofollow">Test</a>""")

	def test_signature_bad_nofollow(self):
		code = """<a href="http://www.linuxos.sk" rel="follow">Test</a>"""
		parser = get_parser('signature')
		parser.parse(code)
		self.assertEqual(parser.get_output(), """<a href="http://www.linuxos.sk" rel="nofollow">Test</a>""")

	def test_profile_parser(self):
		code = """<p><img alt="" src="http://www.linuxos.sk/img.png"></p>"""
		parser = get_parser('profile')
		parser.parse(code)
		self.assertEqual(parser.get_output(), code)

	def test_auto_paragraphs(self):
		code = "Paragraph1\n\nParagraph2"
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), "<p>Paragraph1</p>\n\n<p>Paragraph2</p>")

	def test_auto_paragraphs_between(self):
		code = "<blockquote>BQ</blockquote>Paragraph"
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), "<blockquote>BQ</blockquote><p>Paragraph</p>")

	def test_attr_entity(self):
		code = """<p><a href="http://linuxos.sk/a&amp;b">Test</a></p>"""
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), """<p><a href="http://linuxos.sk/a&amp;b">Test</a></p>""")

	def test_code_class(self):
		code = """<pre class="code-cpp">cpp</pre>"""
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), """<pre class="code-cpp">cpp</pre>""")
		code = """<pre class="wrong">wrong</pre>"""
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), """<pre>wrong</pre>""")

	def test_id(self):
		code = """<p id="test"><a href="#test">link</a>test</p>"""
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), """<p><a href="#test">link</a>test</p>""")
		self.parser.allow_id = True
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), code)
		self.parser.allow_id = 'safe'
		self.parser.parse(code)
		self.assertEqual(self.parser.get_output(), """<p id="content_test"><a href="#content_test">link</a>test</p>""")

	def test_simple_highlight(self):
		code = """<pre class="code-python"># comment &amp; <strong>ta<!-- x -->g</strong>s</pre>"""
		self.assertEqual(highlight_pre_blocks(code), '<pre class="code-python"><span class="c1"># comment &amp; <strong>tag</strong>s</span></pre>')

	def test_cross_highlight(self):
		code = """<pre class="code-python">def <strong>fn(</strong>):</pre>"""
		self.assertEqual(highlight_pre_blocks(code), '<pre class="code-python"><span class="k">def</span> <strong><span class="nf">fn</span><span class="p">(</span></strong><span class="p">):</span></pre>')
		code = """<pre class="code-python">de<strong>f f</strong>n():</pre>"""
		self.assertEqual(highlight_pre_blocks(code), '<pre class="code-python"><span class="k">de<strong>f</strong></span><strong> <span class="nf">f</span></strong><span class="nf">n</span><span class="p">():</span></pre>')
