# -*- coding: utf-8 -*-
import random
from datetime import datetime, timedelta

from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import urlencode
from django.template.defaulttags import date
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone, formats
from django.utils.encoding import force_str
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django_jinja import library

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
