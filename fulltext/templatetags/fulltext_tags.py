# -*- coding: utf-8 -*-
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django_jinja import library

from ..api import highlight


@library.global_function
def fulltext_highlight(text, max_length=None):
	text = escape(text)
	highlighted = highlight(text, '<span class="highlighted">', '</span>', length=max_length)
	return mark_safe(highlighted)
