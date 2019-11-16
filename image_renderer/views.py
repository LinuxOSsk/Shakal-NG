# -*- coding: utf-8 -*-
import os

from PIL import Image, ImageFont
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
		return self.render_node(bg, (0, 0) + bg.size, layout)

	def render_node(self, bg, window, node):
		node = node.copy()
		node_type = node.pop('type')
		return getattr(self, f'render_{node_type}')(bg, window, **node)

	def render_row(self, bg, window, children=None):
		children = [] if children is None else children
		for child in children:
			child_window = self.render_node(bg, window, child)
			window = (window[0], window[1] + child_window[3], window[2], window[3] - child_window[3])
		return window

	def render_text(self, bg, window, text, width=None, height=None):
		width = window[2] if width is None else width
		height = window[3] if height is None else height
		font = ImageFont.truetype(os.path.join(STATIC_DIR, 'fonts', 'OpenSans', 'OpenSans-ExtraBold.ttf'), size=75)
		block = Block(text, (width, height), color='#ffffff', font=font, ellipsis='…')
		result = block.render()
		bg.alpha_composite(result.image, dest=(window[0], window[1]))
		window = (window[0], window[1], result.size[0], result.size[1])
		return window

	def render_canvas(self, bg, window, width=None, height=None): # pylint: disable=unused-argument
		width = window[2] if width is None else width
		height = window[3] if height is None else height
		window = (window[0], window[1], width, height)
		return window

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
					'height': 103,
					'text': self.title,
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
