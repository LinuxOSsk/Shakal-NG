# -*- coding: utf-8 -*-
from django import template
from django_jinja import library
from jinja2 import contextfunction

from notifications.models import Inbox


register = template.Library()


@library.global_function
@contextfunction
@register.assignment_tag(takes_context = True)
def get_unread_notifications(context):
	user = context['request'].user
	if user.is_authenticated():
		return Inbox.objects.user_messages(user).filter(readed = False, event__level__gt = 0)[:99]
	else:
		return Inbox.objects.none()
