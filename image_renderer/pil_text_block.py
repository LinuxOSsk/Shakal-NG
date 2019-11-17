# -*- coding: utf-8 -*-
from collections import namedtuple

from PIL import Image, ImageDraw


class Token(object):
	__slots__ = ['text', 'is_whitespace', 'options']

	def __init__(self, text, is_whitespace=False, options=None):
		self.text = text
		self.is_whitespace = is_whitespace
		self.options = options

	def __repr__(self):
		return f'Token(text={self.text!r}, is_whitespace={self.is_whitespace!r}, options={self.options!r})'


class WordTokenizer(object):
	def __init__(self, text):
		self._text = text

	def get_tokens(self):
		words = self._text.split()
		if not words:
			yield Token(self._text)
		else:
			yield Token(words[0])
		for word in words[1:]:
			yield Token(' ', is_whitespace=True)
			yield Token(word)

	def __repr__(self):
		return f'WordTokenizer(text={self._text!r})'


RenderResult = namedtuple('RenderResult', ('image', 'size'))
TextFragment = namedtuple('TextFragment', ('text', 'color', 'font', 'position', 'size'))


class Block(object):
	__slots__ = [
		'_size', '_tokenizer', '_image', '_draw', '_color', '_font', '_max_lines', '_ellipsis'
	]

	def __init__(self, text, size, color, font, max_lines=None, ellipsis=''):
		self._size = size
		self._tokenizer = WordTokenizer(text)
		self._color = color
		self._font = font
		self._max_lines = max_lines
		self._ellipsis = ellipsis

	def __repr__(self):
		return f'Block(width={self.width!r}, height={self.height!r})'

	def get_text_fragments(self):
		current_line = 0
		current_x = 0
		overflow = False
		line_height = sum(self._font.getmetrics())
		line_buffer = []
		for token in self._tokenizer.get_tokens():
			font = self._font
			size = font.getsize(token.text)
			if current_x == 0:
				line_buffer.append(TextFragment(
					token.text,
					self._color,
					self._font,
					(current_x, current_line * line_height),
					(size[0], line_height)
				))
				current_x += size[0]
			else:
				if current_x + size[0] > self._size[0]:
					if token.is_whitespace:
						continue
					if self._max_lines is not None and (current_line + 1) >= self._max_lines or (current_line + 2) * line_height > self._size[1]:
						overflow = True
						break
					current_line += 1
					current_x = 0
					yield from line_buffer
					line_buffer = []
				line_buffer.append(TextFragment(
					token.text,
					self._color,
					self._font,
					(current_x, current_line * line_height),
					(size[0], line_height)
				))
				current_x += size[0]
		if overflow:
			ellipsis_size = font.getsize(self._ellipsis)
			# remove tokens until free space for ellipsis exist
			while line_buffer:
				last = line_buffer[-1]
				if last.position[0] + last.size[0] + ellipsis_size[0] <= self._size[0]:
					break
				line_buffer.pop()
				current_x = last.position[0]
			yield from  line_buffer
			yield TextFragment(
				self._ellipsis,
				self._color,
				self._font,
				(current_x, current_line * line_height),
				(ellipsis_size[0], line_height)
			)
		else:
			yield from line_buffer

	def render(self):
		self._image = Image.new('RGBA', self._size)
		self._draw = ImageDraw.Draw(self._image)
		final_w, final_h = (0, 0)
		for fragment in self.get_text_fragments():
			# transparent background
			self._draw.rectangle(
					(
						(fragment.position[0], fragment.position[1]),
						(fragment.position[0] + fragment.size[0], fragment.position[1] + fragment.size[1]),
					),
					self._color[:7] + '00'
				)
			# render text
			self._draw.text(
				fragment.position,
				fragment.text,
				fill=fragment.color,
				font=fragment.font
			)
			final_w = max(final_w, fragment.position[0] + fragment.size[0])
			final_h = max(final_h, fragment.position[1] + fragment.size[1])
		final_w = min(self._size[0], final_w)
		final_h = min(self._size[1], final_h)
		self._image = self._image.crop((0, 0, final_w, final_h))
		result = RenderResult(self._image, (final_w, final_h))
		self._image = None
		self._draw = None
		return result
