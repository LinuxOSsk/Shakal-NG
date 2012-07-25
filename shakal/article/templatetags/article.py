# -*- coding: utf-8 -*-

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def content(article):
	content = article.content.replace('<<ANOTACIA>>', '<div class="annotation">' + article.annotation + '</div>')
	return mark_safe(content)
