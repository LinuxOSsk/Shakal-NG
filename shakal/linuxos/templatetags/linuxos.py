# -*- coding: utf-8 -*-

from django import template
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
