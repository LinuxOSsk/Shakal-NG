# -*- coding: utf-8 -*-
from django import template
from django.template.loader import render_to_string
from django_jinja import library
from django.utils.safestring import mark_safe
from jinja2 import contextfunction

from news.models import News


register = template.Library()
lib = library.Library()


@lib.global_function
@contextfunction
@register.simple_tag(takes_context=True)
def news_frontpage(context):
	ctx = {
		'news': News.objects.all()[:10],
		'user': context['user']
	}
	return mark_safe(render_to_string('news/block_news_list.html', ctx))
