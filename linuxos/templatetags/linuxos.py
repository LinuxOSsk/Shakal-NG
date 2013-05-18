# -*- coding: utf-8 -*-
from datetime import timedelta

from django import template
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def humandatetime(value, default = ''):
	try:
		today = timezone.now().date()
		value = timezone.localtime(value)
		if value.year != today.year:
			return mark_safe(value.strftime("%d.%m.%Y&nbsp;|&nbsp;%H:%M"))
		else:
			if today == value.date():
				return mark_safe("Dnes&nbsp;|&nbsp;" + value.strftime("%H:%M"))
			elif (today - timedelta(days = 1)) == value.date():
				return mark_safe("Včera&nbsp;|&nbsp;" + value.strftime("%H:%M"))
			else:
				return mark_safe(value.strftime("%d.%m&nbsp;|&nbsp;%H:%M"))
	except Exception:
		return default


@register.simple_tag
def user_link(user_object, username):
	if user_object:
		template_text = '<a class="url fn" href="{{ link }}">{{ label }}</a>'
		tpl = template.Template(template_text)
		ctx = template.Context({'link': user_object.get_absolute_url(), 'label': str(user_object)})
		return tpl.render(ctx)
	else:
		return escape(username)


class MessagesNode(template.Node):
	def __init__(self, messages, tags):
		self.messages = messages
		self.tags = tags

	def render(self, context):
		messages = template.resolve_variable(self.messages, context)
		tags = [template.resolve_variable(tag, context) for tag in self.tags]
		if not tags:
			messages = self.__filter_exact_tags(messages, ['debug', 'info', 'success', 'warning', 'error'])
		else:
			messages = self.__filter_contains_tags(messages, tags)
		search_templates = []
		if tags:
			search_templates.append('messages/messages_' + '_'.join(tags) + '.html')
		search_templates.append('messages/messages.html')
		return render_to_string(search_templates, {'messages': messages})

	def __filter_exact_tags(self, messages, tags):
		new_messages = []
		for message in messages:
			if message.tags in tags:
				new_messages.append(message)
		return new_messages

	def __filter_contains_tags(self, messages, tags):
		new_messages = []
		for message in messages:
			if message.tags:
				message_tags = message.tags.split(' ')
				for message_tag in message_tags:
					if message_tag in tags:
						new_messages.append(message)
						break
		return new_messages


@register.tag
def render_messages(parser, token):
	parts = token.split_contents()
	if len(parts) < 2:
		raise template.TemplateSyntaxError('{0} tags requires messages variable.'.format(token.contents.split()[0]))
	return MessagesNode(parts[1], parts[2:])


@register.filter
def labelize_content_type(content_type):
	app_label, model = content_type.split('.')
	return ContentType.objects.get_by_natural_key(app_label = app_label, model = model).model_class()._meta.verbose_name
