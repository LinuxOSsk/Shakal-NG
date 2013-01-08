# -*- coding: utf-8 -*-

from django.utils.html import strip_tags
from haystack.utils.highlighting import Highlighter
import re

class XapianHighlighter(Highlighter):
	def __init__(self, query, **kwargs):
		super(XapianHighlighter, self).__init__(query, **kwargs)

	def highlight(self, text_block):
		try:
			text, xapian_text = text_block.split('<xapian>')
		except ValueError:
			text = text_block
			xapian_text = None

		self.text_block = strip_tags(text)
		highlight_locations = self.find_highlightable_words()
		count_highlights = sum((len(h[1])) for h in highlight_locations.iteritems())
		if count_highlights or xapian_text is None:
			start_offset, end_offset = self.find_window(highlight_locations)
			return self.render_html(highlight_locations, start_offset, end_offset)

		self.query_words = set(re.findall('<em>Z([^<]+)<\/em>', xapian_text))
		self.text_block = strip_tags(xapian_text.replace('<em>Z', '<em>'))

		highlight_locations = self.find_highlightable_words()
		start_offset, end_offset = self.find_window(highlight_locations)
		return self.render_html(highlight_locations, start_offset, end_offset)

	def find_window(self, highlight_locations):
		if not self.max_length:
			return (0, len(self.text_block))
		else:
			window = super(XapianHighlighter, self).find_window(highlight_locations)
			if (window[1] >= len(self.text_block)):
				diff = window[1] - len(self.text_block)
				w1 = window[1] - diff
				w0 = max(window[0] - diff, 0)
				window = (w0, w1)
			return window
