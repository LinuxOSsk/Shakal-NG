# -*- coding: utf-8 -*-
import re

from bleach.sanitizer import Cleaner
from django.template.defaultfilters import linebreaks_filter
from django.utils.html import escape
from html5lib.filters import base
from html5lib.filters import alphabeticalattributes


class AddRequiredAttributesFilter(base.Filter):
	def __iter__(self):
		for token in base.Filter.__iter__(self):
			if token['type'] == 'StartTag':
				if token['name'] == 'a':
					token['data'].setdefault((None, 'href'), '#')
				if token['name'] == 'img':
					token['data'].setdefault((None, 'src'), '#')
					token['data'].setdefault((None, 'alt'), '')
			yield token


class AddNofollowFilter(base.Filter):
	def __iter__(self):
		for token in base.Filter.__iter__(self):
			if token['type'] == 'StartTag':
				if token['name'] == 'a':
					token['data'][(None, 'rel')] = 'nofollow'
			yield token


class ClassFilter(base.Filter):
	CODE_RX = re.compile(r'^code-\w+$')

	def __iter__(self):
		for token in base.Filter.__iter__(self):
			if token['type'] == 'StartTag':
				if token['name'] == 'pre' and (None, 'class') in token['data']:
					if not self.CODE_RX.match(token['data'][(None, 'class')]):
						token['data'].pop((None, 'class'), None)
				else:
					token['data'].pop((None, 'class'), None)
			yield token


class AutoParagraphFilter(base.Filter):
	PARAGRAPH_RX = re.compile(r'(\n\n+)')

	def __iter__(self):
		inside_block_tags = 0
		inside_auto_paragraph = False
		for token in base.Filter.__iter__(self):
			if token['type'] == 'StartTag' and token['name'] not in FULL_TEXT_TAGS_LIST: # leave auto paragraph mode
				inside_block_tags += 1
				if inside_auto_paragraph:
					inside_auto_paragraph = False
					yield {'name': 'p', 'type': 'EndTag', 'namespace': None}

			if not inside_auto_paragraph and not inside_block_tags: # enter auto paragraph mode
				if (token['type'] == 'StartTag' and token['name'] in FULL_TEXT_TAGS_LIST) or (token['type'] == 'Characters' and token['data'].strip()):
					inside_auto_paragraph = True
					yield {'name': 'p', 'type': 'StartTag', 'data': {}, 'namespace': None}

			if inside_auto_paragraph and token['type'] == 'Characters':
				yield from self.text_to_pagagraphs(token['data'])
			else:
				yield token

			if token['type'] == 'EndTag' and token['name'] not in FULL_TEXT_TAGS_LIST:
				inside_block_tags -= 1

		if inside_auto_paragraph:
			yield {'name': 'p', 'type': 'EndTag', 'namespace': None}

	def text_to_pagagraphs(self, text):
		parts = self.PARAGRAPH_RX.split(text)
		for part in parts:
			is_split = self.PARAGRAPH_RX.match(part)
			if is_split:
				yield {'name': 'p', 'type': 'EndTag', 'namespace': None}
			yield {'type': 'Characters', 'data': part}
			if is_split:
				yield {'name': 'p', 'type': 'StartTag', 'data': {}, 'namespace': None}


ALL_TAGS = ['a', 'abbr', 'acronym', 'address', 'applet', 'area', 'article', 'aside', 'audio', 'b', 'base', 'basefont', 'bdi', 'bdo', 'big', 'blockquote', 'body', 'br', 'button', 'canvas', 'caption', 'center', 'cite', 'code', 'col', 'colgroup', 'command', 'datalist', 'dd', 'del', 'details', 'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'embed', 'fieldset', 'figcaption', 'figure', 'font', 'footer', 'form', 'frame', 'frameset', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'header', 'hgroup', 'hr', 'html', 'i', 'iframe', 'img', 'input', 'ins', 'kbd', 'keygen', 'label', 'legend', 'li', 'link', 'map', 'mark', 'menu', 'meta', 'meter', 'nav', 'noframes', 'noscript', 'object', 'ol', 'optgroup', 'option', 'output', 'p', 'param', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby', 's', 'samp', 'script', 'section', 'select', 'small', 'source', 'span', 'strike', 'strong', 'style', 'sub', 'summary', 'sup', 'table', 'tbody', 'td', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title', 'tr', 'track', 'tt', 'u', 'ul', 'var', 'video', 'wbr']


TEXT_TAGS_LIST = ['b', 'u', 'i', 'em', 'strong', 'a', 'br', 'del', 'ins', 'sub', 'sup']
ONELINE_TAGS_LIST = ['b', 'u', 'i', 'em', 'strong', 'a']
FULL_TEXT_TAGS_LIST = ['b', 'u', 'i', 'em', 'strong', 'a', 'br', 'del', 'ins', 'abbr', 'img', 'sub', 'sup']
FULL_TAGS_LIST = ['b', 'u', 'i', 'em', 'strong', 'a', 'pre', 'p', 'span', 'br', 'del', 'ins', 'sub', 'sup', 'code', 'blockquote', 'cite', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'dl', 'dt', 'dd', 'abbr', 'img', 'table', 'thead', 'tbody', 'tfoot', 'caption', 'tr', 'th', 'td']
DEFAULT_TAG_LIST = ['b', 'u', 'i', 'em', 'strong', 'a', 'pre', 'p', 'span', 'br', 'del', 'ins', 'abbr', 'img', 'sub', 'sup', 'code', 'blockquote', 'cite', 'ol', 'ul', 'li']
ALLOWED_ATTRIBUTES = {
	'a': ['href', 'title', 'nofollow'],
	'abbr': ['title'],
	'acronym': ['title'],
	'img': ['src', 'alt'],
	'th': ['colspan', 'rowspan'],
	'td': ['colspan', 'rowspan'],
	'pre': ['class'],
}


class HtmlParser:
	auto_paragraphs = True
	add_nofollow = True
	cleaner = None

	def __init__(self, supported_tags=None):
		if supported_tags is None:
			supported_tags = DEFAULT_TAG_LIST
		else:
			supported_tags = supported_tags
		self.cleaner = Cleaner(tags=supported_tags, attributes=ALLOWED_ATTRIBUTES)

	def parse(self, text):
		filters = [AddRequiredAttributesFilter, ClassFilter, alphabeticalattributes.Filter]
		if self.auto_paragraphs:
			filters.append(AutoParagraphFilter)
		if self.add_nofollow:
			filters.append(AddNofollowFilter)
		self.cleaner.filters = filters
		output = self.cleaner.clean(text)
		self.output = output

	def get_output(self):
		return self.output

	def get_attributes(self):
		return {}

	@property
	def supported_tags(self):
		return self.cleaner.tags


class RawParser:
	def parse(self, text):
		self.output = text

	def get_output(self):
		return self.output

	def get_attributes(self):
		return {}


class TextParser:
	def parse(self, text):
		self.output = linebreaks_filter(escape(text))

	def get_output(self):
		return self.output

	def get_attributes(self):
		return {}
