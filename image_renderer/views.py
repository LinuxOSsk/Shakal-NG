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

	def render_column(self, size, children=None, padding_top=0, padding_right=0, padding_bottom=0, padding_left=0, spacing=0):
		return self._render_on_axis(0, size, children, padding_top, padding_right, padding_bottom, padding_left, spacing)

	def render_row(self, size, children=None, padding_top=0, padding_right=0, padding_bottom=0, padding_left=0, spacing=0):
		return self._render_on_axis(1, size, children, padding_top, padding_right, padding_bottom, padding_left, spacing)

	def _render_on_axis(self, axis, size, children=None, padding_top=0, padding_right=0, padding_bottom=0, padding_left=0, spacing=0):
		if size[0] <= 0 or size[1] <= 0:
			return
		image = Image.new('RGBA', size)
		children = [] if children is None else children
		total_spacing = max((len(children) - 1) * spacing, 0)
		size = (size[0] - padding_left - padding_right, size[1] - padding_top - padding_bottom)
		if axis == 0:
			size = (size[0] - total_spacing, size[1])
		else:
			size = (size[0], size[1] - total_spacing)
		if size[0] <= 0 or size[1] <= 0:
			return
		initial_axis_size = size[axis]
		image_buffers = []
		for child in children:
			child = child.copy()
			stretch = child.pop('stretch', None)
			if stretch is None:
				child_image = self.render_node(size, child)
				axis_size = 0
				if child_image is not None:
					axis_size = child_image.size[axis]
					image_buffers.append({'image': child_image, 'size': axis_size})
				if axis == 0:
					size = (size[0] - axis_size, size[1])
				else:
					size = (size[0], size[1] - axis_size)
			else:
				image_buffers.append({'stretch': stretch, 'child': child})

		self._calculate_buffer_positions(image_buffers, initial_axis_size, spacing)

		for buf in image_buffers:
			if 'child' in buf:
				if axis == 0:
					buf['image'] = self.render_node((buf['size'], size[1]), buf['child'])
				else:
					buf['image'] = self.render_node((size[0], buf['size']), buf['child'])
			if buf.get('image'):
				if axis == 0:
					image.alpha_composite(buf['image'], dest=(buf['position'] + padding_left, padding_top))
				else:
					image.alpha_composite(buf['image'], dest=(padding_left, buf['position'] + padding_top))

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

	def _calculate_buffer_positions(self, buffers, size, spacing):
		fixed_size = 0
		stretch_count = 0
		for buf in buffers:
			fixed_size += buf.get('size', 0)
			stretch_count += buf.get('stretch', 0)

		free_size = max(size - fixed_size, 0)
		start_position = 0
		for buf in buffers:
			child = buf.get('child')
			stretch = buf.get('stretch', 0)
			if child is not None:
				size = (free_size * (stretch + start_position)) // stretch_count - (free_size * start_position) // stretch_count
				start_position += stretch
				buf['size'] = size

		start_position = 0
		for buf in buffers:
			buf['position'] = start_position
			start_position += buf['size'] + spacing


class TextRenderer(BaseRenderer):
	def __init__(self, image_type, content_type, content_object, content_field, title_field):
		self.content = getattr(content_object, content_field)
		self.title = getattr(content_object, title_field)
		super().__init__(image_type, content_type, content_object)

	def render(self):
		bg = self.get_background_image()
		layout = {
			'type': 'row',
			'padding_left': 20,
			'padding_top': 20,
			'padding_right': 20,
			'padding_bottom': 20,
			'spacing': 20,
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
					'text': 'World',
					'stretch': 1,
					'font_size': 48,
				},
				{
					'type': 'canvas',
					'height': 20,
				},
				{
					'type': 'canvas',
					'height': 20,
				},
				{
					'type': 'canvas',
					'height': 20,
				},
				{
					'type': 'text',
					'text': "oooooo",
					'font': 'OpenSans/OpenSans-ExtraBold.ttf',
					'font_size': 48,
					'color': '#ffffff',
					'max_lines': 2,
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
