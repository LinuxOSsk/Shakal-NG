# -*- coding: utf-8 -*-
from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django_jinja import library
from jinja2 import contextfunction


register = template.Library()
lib = library.Library()


def render_feed_list(feeds, template):
	return mark_safe(render_to_string(template, {'feeds': feeds}))


@lib.global_function
@contextfunction
@register.simple_tag(takes_context=True)
def render_feeds(context, object_type=None, object_id=None, template='feeds/feeds.html'):
	feeds = context.get('feeds', [])
	filtered_feeds = filter(lambda f: f['object_type'] == object_type and f['object_id'] == object_id, feeds)
	return render_feed_list(filtered_feeds, template)


@lib.global_function
@contextfunction
@register.simple_tag(takes_context=True)
def render_all_feeds(context, template='feeds/feeds.html'):
	feeds = context.get('feeds', [])
	return render_feed_list(feeds, template)
