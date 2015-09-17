# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.safestring import mark_safe
from django_jinja import library
from haystack.utils import Highlighter


@library.global_function
def highlight(text_block, query, **kwargs):
	highlighter = Highlighter(query, **kwargs)
	highlighted_text = highlighter.highlight(text_block)
	return mark_safe(highlighted_text)
