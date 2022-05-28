# -*- coding: utf-8 -*-
import json
import random
from collections import OrderedDict
from datetime import datetime, timedelta

from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import QueryDict
from django.template.defaultfilters import urlencode
from django.template.defaulttags import date
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone, formats
from django.utils.encoding import force_str
from django.utils.html import format_html, escape
from django.utils.safestring import mark_safe
from django_jinja import library
from jinja2 import pass_context

from attachment.models import AttachmentImage
from common_utils import get_meta
from common_utils.random import weighted_sample
from rating.settings import FLAG_CONTENT_TYPES


register = template.Library()


@library.filter
@register.filter
def humandatetime(value, default='', separator='&nbsp;|&nbsp;'):
	if not value:
		return default
	today = timezone.localtime(timezone.now()).date()
	value = timezone.localtime(value)
	if value.year != today.year:
		return mark_safe(value.strftime("%d.%m.%Y" + separator + "%H:%M"))
	else:
		if today == value.date():
			return mark_safe("Dnes" + separator + value.strftime("%H:%M"))
		elif (today - timedelta(days=1)) == value.date():
			return mark_safe("Včera" + separator + value.strftime("%H:%M"))
		else:
			return mark_safe(value.strftime("%d.%m" + separator + "%H:%M"))


@library.global_function
@register.simple_tag
def user_link(user_object, username=None):
	if user_object:
		if user_object.is_active:
			return format_html('<a class="url fn" href="{0}" rel="nofollow">{1}</a>', user_object.get_absolute_url(), force_str(user_object))
		else:
			return force_str(user_object)
	else:
		if username:
			return escape(username)
		else:
			return '-'


@library.global_function
@register.simple_tag()
def render_messages(messages, *tags):
	def filter_exact_tags(messages, tags):
		new_messages = []
		for message in messages:
			if message.tags in tags:
				new_messages.append(message)
		return new_messages

	def filter_contains_tags(messages, tags):
		new_messages = []
		for message in messages:
			if message.tags:
				message_tags = message.tags.split(' ')
				for message_tag in message_tags:
					if message_tag in tags:
						new_messages.append(message)
						break
		return new_messages

	if not tags:
		messages = filter_exact_tags(messages, ['debug', 'info', 'success', 'warning', 'error'])
	else:
		messages = filter_contains_tags(messages, tags)
	search_templates = []
	if tags:
		search_templates.append('messages/messages_' + '_'.join(tags) + '.html')
	search_templates.append('messages/messages.html')
	return mark_safe(render_to_string(search_templates, {'messages': messages}))


@library.filter
@register.filter
def labelize_content_type(content_type):
	app_label, model = content_type.split('.')
	return get_meta(ContentType.objects.get_by_natural_key(app_label=app_label, model=model).model_class()).verbose_name


@library.global_function
@register.simple_tag()
def get_base_uri():
	return settings.BASE_URI


@library.global_function
def firstof(*args):
	for arg in args:
		if arg:
			return arg
	return ''


@library.global_function
def now(format_string):
	tzinfo = timezone.get_current_timezone() if settings.USE_TZ else None
	return date(datetime.now(tz=tzinfo), format_string)


@library.filter
def urlquote(string):
	return urlencode(string, '')


@library.global_function
def flag_url(obj):
	ctype = ContentType.objects.get_for_model(obj.__class__)
	if (ctype.app_label, ctype.model) not in FLAG_CONTENT_TYPES:
		return
	return reverse('rating:flag', kwargs={'content_type': ctype.pk, 'object_id': obj.pk})


@library.global_function
def share_image(obj, image_type):
	ctype = ContentType.objects.get_for_model(obj.__class__)
	return reverse('image_renderer:render', kwargs={'image_type': image_type, 'content_type': ctype.pk, 'object_id': obj.pk})


@library.filter
def number_format(value):
	return formats.number_format(value)


@library.filter
def shuffle(items):
	items = list(items)
	random.shuffle(items)
	return items


@library.filter
def shuffle_with_time_priority(items, max_count=None):
	if max_count is None:
		max_count = len(items)
	now = timezone.now()
	weights = [7 * 86400 / (min(max((now - item.created).total_seconds(), 0), 86400 * 90) + 86400 * 3) for item in items]
	return weighted_sample(items, weights, max_count)


@library.filter
def sort_newest_first(items):
	return sorted(items, key=lambda item: item.updated, reverse=True)


@library.global_function
@pass_context
def change_template_settings_form(context, **settings):
	request = context['request']
	current_style = context['current_style']
	style_options = (context['style_options'] or {}).copy()
	style_css = context['style_css']
	for key, value in settings.items():
		if value is None:
			style_options.pop(key, None)
		else:
			style_options[key] = value
	return format_html(
		''.join(f'<input name="{name}" type="hidden" value="{{}}" />' for name in ['template', 'css', 'settings', 'next']),
		current_style,
		style_css,
		json.dumps(style_options),
		request.get_full_path()
	)


@library.global_function
@pass_context
def get_share_images(context):
	request = context['request']
	images = OrderedDict()
	presentation_image = context.get('presentation_image')
	fallback_image = context.get('fallback_image')
	fallback_image2 = context.get('fallback_image2')
	image = context.get('image')
	gallery = context.get('gallery')
	obj = context.get('object')

	def register_image(image):
		if isinstance(image, AttachmentImage):
			images[image.attachment.url] = {
				'url': get_base_uri() + image.attachment.url,
				'width': image.width,
				'height': image.height,
			}
		elif isinstance(image, dict):
			url = image['url']
			image['url'] = get_base_uri() + url
			images[url] = image

		else:
			images.setdefault(image, {'url': get_base_uri() + image})

	if 'share_image' in request.GET:
		images.setdefault(request.GET['share_image'], {'url': request.GET['share_image']})
	if presentation_image:
		register_image(presentation_image)
	if image:
		register_image(image)
	if fallback_image:
		register_image(fallback_image)
	if fallback_image2:
		register_image(fallback_image2)
	if gallery:
		register_image(gallery[0])
	if obj:
		url = share_image(obj, 'opengraph')
		register_image({
			'url': url,
			'width': 1200,
			'height': 630,
		})
	if gallery:
		for image in gallery[1:]:
			register_image(image)
	if not images:
		url = settings.STATIC_URL + 'images/share_placeholder.png'
		register_image({
			'url': url,
			'width': 2048,
			'height': 1024,
		})
	return list(images.values())


@library.global_function
@pass_context
def get_share_canonical_url(context):
	request = context['request']
	q = QueryDict('', mutable=True)
	if 'share_image' in request.GET:
		q['share_image'] = request.GET['share_image']
	if q:
		q = '?' + q.urlencode()
	else:
		q = ''
	return request.path + q
