# -*- coding: utf-8 -*-

from django import template
from django.template.loader import render_to_string
from django.utils.html import escape
from datetime import date, timedelta

register = template.Library()


@register.filter
def humandatetime(value):
	try:
		today = date.today()
		if value.year != today.year:
			return value.strftime("%d.%m.%Y | %H:%M")
		else:
			if today == value.date():
				return "Dnes | " + value.strftime("%H:%M")
			elif (today - timedelta(days = 1)) == value.date():
				return "Včera | " + value.strftime("%H:%M")
			else:
				return value.strftime("%d.%m | %H:%M")
	except Exception:
		return ""


@register.simple_tag
def user_link(user_object, username):
	if user_object:
		template_text = '<a href="{{ link }}">{{ label }}</a>'
		user_label = user_object.username
		if user_object.get_full_name():
			user_label = user_object.get_full_name()
		tpl = template.Template(template_text)
		ctx = template.Context({'link': user_object.get_absolute_url(), 'label': user_label})
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
