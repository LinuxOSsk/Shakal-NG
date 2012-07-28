# -*- coding: utf-8 -*-

from django import template
from django.utils.html import escape
from datetime import date, timedelta

register = template.Library()

@register.filter
def humandatetime(value):
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
