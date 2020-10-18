# -*- coding: utf-8 -*-
import os

from PIL import Image, ImageFont, ImageDraw
from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponseNotFound, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import date as date_filter, striptags
from django.utils import timezone
from django.utils.encoding import force_str
from django.views.generic import View
from easy_thumbnails.files import get_thumbnailer

from .pil_text_block import Block
from fulltext.templatetags.html_entity_decode import html_entity_decode


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

	def render_column(self, size, children=None, padding_top=0, padding_right=0, padding_bottom=0, padding_left=0, spacing=0, height=None):
		return self._render_on_axis(0, size, children, padding_top, padding_right, padding_bottom, padding_left, spacing, height)

	def render_row(self, size, children=None, padding_top=0, padding_right=0, padding_bottom=0, padding_left=0, spacing=0, width=None):
		return self._render_on_axis(1, size, children, padding_top, padding_right, padding_bottom, padding_left, spacing, width)

	def _render_on_axis(self, axis, size, children=None, padding_top=0, padding_right=0, padding_bottom=0, padding_left=0, spacing=0, secondary_axis_size=None):
		if secondary_axis_size is not None:
			if axis == 0:
				size = (size[0], secondary_axis_size)
			else:
				size = (secondary_axis_size, size[1])
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

		output_width = 0
		output_height = 0

		for buf in image_buffers:
			if 'child' in buf:
				if axis == 0:
					buf['image'] = self.render_node((buf['size'], size[1]), buf['child'])
				else:
					buf['image'] = self.render_node((size[0], buf['size']), buf['child'])
			if buf.get('image'):
				if axis == 0:
					dest = (buf['position'] + padding_left, padding_top)
				else:
					dest = (padding_left, buf['position'] + padding_top)
				output_width = max(dest[0] + buf['image'].size[0], output_width)
				output_height = max(dest[1] + buf['image'].size[1], output_height)
				image.alpha_composite(buf['image'], dest=dest)

		return image.crop((0, 0, output_width, output_height))

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

	def render_canvas(self, size, width=None, height=None, draw_function=None, **kwargs):
		width = size[0] if width is None else width
		height = size[1] if height is None else height
		if width <= 0 or height <= 0:
			return
		image = Image.new('RGBA', (width, height))
		if draw_function is not None:
			draw_function(image, **kwargs)
		return image

	def render_rule(self, size, color, padding_top=0, padding_bottom=0):
		image = Image.new('RGBA', (size[0], 1 + padding_top + padding_bottom))
		draw = ImageDraw.Draw(image)
		draw.rectangle(((0, padding_top), (size[0], padding_top)), fill=color)
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

	def draw_image(self, image):
		thumbnailer = get_thumbnailer(self.image)
		thumbnail = thumbnailer.generate_thumbnail({
			'size': (128, 128),
			'upscale': True,
		})
		im = thumbnail.image.convert('RGBA')
		image.alpha_composite(im, dest=((128 - im.size[0]) // 2, (128 - im.size[1]) // 2 + 10))


NOT_SET = object()


class TextRenderer(BaseRenderer):
	def __init__(self, image_type, content_type, content_object, content_field, title_field, category_field=None, image_field=None):
		self.object = content_object
		self.content = ''
		if content_field is not None:
			self.content = self.getattr(content_object, content_field)
		self.title = self.getattr(content_object, title_field)
		self.category = None
		if category_field is not None:
			self.category = force_str(self.getattr(content_object, category_field))
		self.image = None
		if image_field is not None:
			self.image = force_str(self.getattr(content_object, image_field))
		self.created = self.getattr(content_object, 'created', None)
		self.content = html_entity_decode(striptags(self.content))
		super().__init__(image_type, content_type, content_object)

	def getattr(self, content_object, attr, default=NOT_SET):
		default_is_set = default is not NOT_SET
		if not hasattr(content_object, attr) and '__' in attr:
			prefix, suffix = attr.split('__', 1)
			if default_is_set:
				content_object = getattr(content_object, prefix, default)
			else:
				content_object = getattr(content_object, prefix)
			return self.getattr(content_object, suffix)
		if default_is_set:
			return getattr(content_object, attr, default)
		else:
			return getattr(content_object, attr)

	def get_layout(self):
		info_items = []
		info_layout = {
			'type': 'column',
			'children': info_items,
		}
		if self.created is not None:
			info_items.append({
				'type': 'text',
				'text': date_filter(timezone.localtime(self.created), 'SHORT_DATE_FORMAT'),
				'font': 'OpenSans/OpenSans-Regular.ttf',
				'font_size': 26,
				'color': '#ffffffa0',
			})
			info_items.append({
				'type': 'text',
				'text': '    ',
				'font': 'OpenSans/OpenSans-Regular.ttf',
				'font_size': 26,
				'color': '#ffffffa0',
			})
		if self.category:
			info_items.append({
				'type': 'text',
				'text': self.category,
				'font': 'OpenSans/OpenSans-Regular.ttf',
				'font_size': 26,
				'color': '#ffffff',
				'stretch': 1
			})

		header_layout = [
			{
				'type': 'row',
				'stretch': 1,
				'children': [
					{
						'type': 'text',
						'text': self.title,
						'font': 'OpenSansCondensed/OpenSansCondensed-Bold.ttf',
						'font_size': 48,
						'color': '#ffffff',
						'max_lines': 1,
					},
					info_layout,
					{
						'type': 'rule',
						'color': '#ffffffa0',
						'padding_top': 16,
						'padding_bottom': 6,
					},
				],
			},
		]
		if self.image:
			header_layout.append({
				'type': 'canvas',
				'width': 128,
				'height': 138,
				'draw_function': self.draw_image
			})

		return {
			'type': 'row',
			'padding_left': 30,
			'padding_top': 20,
			'padding_right': 30,
			'padding_bottom': 20,
			'spacing': 0,
			'children': [
				{
					'type': 'column',
					'children': header_layout,
					'spacing': 20,
				},
				{
					'type': 'text',
					'text': self.content,
					'stretch': 1,
					'font_size': 46,
					'font': 'OpenSansCondensed/OpenSansCondensed-Light.ttf',
					'color': '#ffffff',
				},
			]
		}

	def render(self):
		layout = self.get_layout()
		bg = self.get_background_image()
		self.render_layout(bg, layout)
		response = HttpResponse(content_type='image/png')
		bg.convert('RGB').save(response, format='PNG')
		return response


class PollRenderer(TextRenderer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def get_layout(self):
		layout = super().get_layout()
		layout['children'].pop()
		for choice in self.object.choice_set.all():
			layout['children'].append({
				'type': 'text',
				'text': force_str(choice),
				'font_size': 52,
				'font': 'OpenSansCondensed/OpenSansCondensed-Light.ttf',
				'color': '#ffffff',
			})

		return layout


RENDERERS = {
	('opengraph', 'accounts', 'user'): (TextRenderer, {'title_field': 'username', 'content_field': 'info', 'image_field': 'avatar'}),
	('opengraph', 'article', 'article'): (TextRenderer, {'title_field': 'title', 'content_field': 'perex', 'category_field': 'category'}),
	('opengraph', 'news', 'news'): (TextRenderer, {'title_field': 'title', 'content_field': 'short_text', 'category_field': 'category'}),
	('opengraph', 'blog', 'blog'): (TextRenderer, {'title_field': 'title', 'content_field': 'description', 'category_field': 'author'}),
	('opengraph', 'blog', 'post'): (TextRenderer, {'title_field': 'title', 'content_field': 'perex', 'category_field': 'blog__author'}),
	('opengraph', 'desktops', 'desktop'): (TextRenderer, {'title_field': 'title', 'content_field': 'text', 'image_field': 'image', 'category_field': 'author'}),
	('opengraph', 'forum', 'topic'): (TextRenderer, {'title_field': 'title', 'content_field': 'text', 'category_field': 'section'}),
	('opengraph', 'polls', 'poll'): (PollRenderer, {'title_field': 'question', 'content_field': None}),
	('opengraph', 'tweets', 'tweet'): (TextRenderer, {'title_field': 'title', 'content_field': 'text'}),
	('opengraph', 'wiki', 'page'): (TextRenderer, {'title_field': 'title', 'content_field': 'text', 'category_field': 'parent'}),
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
