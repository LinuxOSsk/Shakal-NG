# -*- coding: utf-8 -*-
import os

from PIL import Image, ImageFont, ImageDraw
from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponseNotFound, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from pil_text_block import Block


STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'static')


def get_fallback_response():
	if get_fallback_response.image_cache is None:
		with open(os.path.join(STATIC_DIR, 'images', 'share_text_fallback.png'), 'rb') as fallback_fp:
			get_fallback_response.image_cache = fallback_fp.read()
	return HttpResponse(get_fallback_response.image_cache, content_type='image/png')
get_fallback_response.image_cache = None


class BaseRenderer(object):
	_backgrund_image = None

	def __init__(self, image_type, content_type, content_object):
		self.image_type = image_type
		self.content_type = content_type
		self.content_object = content_object

	def get_background_image(self):
		if self._backgrund_image is None:
			path = os.path.join(STATIC_DIR, 'images', 'share_text_background.png')
			self._backgrund_image = Image.open(path)
		return self._backgrund_image.convert('RGBA')

	def render_layout(self, bg, layout):
		rendered = self.render_node(bg.size, layout)
		if rendered:
			bg.alpha_composite(rendered)
		return bg

	def render_node(self, size, node):
		node = node.copy()
		node_type = node.pop('type')
		return getattr(self, f'render_{node_type}')(size, **node)

	def render_row(self, size, children=None):
		if size[0] <= 0 or size[1] <= 0:
			return
		image = Image.new('RGBA', size)
		children = [] if children is None else children
		y = 0
		image_height = 0
		for child in children:
			child_image = self.render_node(size, child)
			image_height = 0
			if child_image is not None:
				image.alpha_composite(child_image, dest=(0, y))
				image_height= child_image.size[1]
				y += image_height
			print(image_height)
			size = (size[0], size[1] - image_height)
		return image

	def render_text(self, size, text, width=None, height=None, font=None, font_size=None, color=None, max_lines=None):
		width = size[0] if width is None else width
		height = size[1] if height is None else height
		if width <= 0 or height <= 0:
			return
		font = 'OpenSans/OpenSans-Regular.ttf' if font is None else font
		font_size = 32 if font_size is None else font_size
		color = '#000000' if color is None else color
		font = ImageFont.truetype(os.path.join(STATIC_DIR, 'fonts', font.replace('/', os.sep)), size=font_size)
		block = Block(text, (width, height), color=color, font=font, ellipsis='…', max_lines=max_lines)
		result = block.render()
		return result.image

	def render_canvas(self, size, width=None, height=None): # pylint: disable=unused-argument
		width = size[0] if width is None else width
		height = size[1] if height is None else height
		if width <= 0 or height <= 0:
			return
		image = Image.new('RGBA', (width, height))
		draw = ImageDraw.Draw(image)
		draw.rectangle(((0, 0), (width, height)), fill='#ffffff80')
		return image

	def render(self):
		raise NotImplementedError()


class TextRenderer(BaseRenderer):
	def __init__(self, image_type, content_type, content_object, content_field, title_field):
		self.content = getattr(content_object, content_field)
		self.title = getattr(content_object, title_field)
		super().__init__(image_type, content_type, content_object)

	def render(self):
		bg = self.get_background_image()
		layout = {
			'type': 'row',
			'children': [
				{
					'type': 'canvas',
					'height': 20,
				},
				{
					'type': 'text',
					'text': self.title,
					'font': 'OpenSans/OpenSans-ExtraBold.ttf',
					'font_size': 48,
					'color': '#ffffff',
					'max_lines': 2,
				},
				{
					'type': 'canvas',
					'height': 20,
				},
				{
					'type': 'text',
					'text': 'World'
				},
				{
					'type': 'canvas',
					'height': 20,
				},
			]
		}
		self.render_layout(bg, layout)
		response = HttpResponse(content_type='image/png')
		bg.convert('RGB').save(response, format='PNG')
		return response


RENDERERS = {
	('opengraph', 'news', 'news'): (TextRenderer, {'title_field': 'title', 'content_field': 'short_text'}),
}


class RendererFactory():
	@staticmethod
	def get_renderer(image_type, content_type, content_object):
		try:
			renderer_class, kwargs = RENDERERS[(image_type, content_type.app_label, content_type.model)]
		except KeyError:
			return None
		return renderer_class(image_type, content_type, content_object, **kwargs)


class RenderImageView(View):
	def get(self, request, image_type, content_type, object_id):
		content_type = get_object_or_404(ContentType, pk=content_type)
		try:
			content_object = get_object_or_404(content_type.model_class(), pk=object_id)
		except ValueError:
			return HttpResponseNotFound()
		renderer = RendererFactory.get_renderer(image_type, content_type, content_object)
		if renderer is None:
			return get_fallback_response()
		else:
			return renderer.render()
