# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta

from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.template.defaulttags import date
from django.template.defaultfilters import urlencode
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import smart_unicode
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django_jinja import library
from jinja2 import contextfunction

from common_utils import get_meta
from common_utils.middlewares.ThreadLocal import get_current_request


register = template.Library()


@library.filter
@register.filter
def humandatetime(value, default=''):
	if not value:
		return default
	today = timezone.now().date()
	value = timezone.localtime(value)
	if value.year != today.year:
		return mark_safe(value.strftime("%d.%m.%Y&nbsp;|&nbsp;%H:%M"))
	else:
		if today == value.date():
			return mark_safe("Dnes&nbsp;|&nbsp;" + value.strftime("%H:%M"))
		elif (today - timedelta(days=1)) == value.date():
			return mark_safe("Včera&nbsp;|&nbsp;" + value.strftime("%H:%M"))
		else:
			return mark_safe(value.strftime("%d.%m&nbsp;|&nbsp;%H:%M"))


@library.global_function
@register.simple_tag
def user_link(user_object, username):
	if user_object:
		return format_html('<a class="url fn" href="{0}">{1}</a>', user_object.get_absolute_url(), smart_unicode(user_object))
	else:
		return escape(username)


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
@contextfunction
@register.simple_tag(takes_context=True)
def get_base_uri(context):
	if 'request' in context:
		request = context['request']
	else:
		request = get_current_request()
	if request:
		url = request.build_absolute_uri('/')[:-1]
		if url.startswith('http://'):
			url = 'https://' + url[7:]
		return url
	if 'request' in context:
		return context['request'].build_absolute_uri('/')[:-1]
	else:
		return ''


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
