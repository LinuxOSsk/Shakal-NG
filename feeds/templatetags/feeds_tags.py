# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django_jinja import library
from jinja2 import contextfunction


def render_feed_list(feeds, template):
	return mark_safe(render_to_string(template, {'feeds': feeds}))


@library.global_function
@contextfunction
def render_feeds(context, object_type=None, object_id=None, template='feeds/feeds.html'):
	feeds = getattr(context.get('request'), '_feeds', [])
	return render_feed_list([f for f in feeds if f['object_type'] == object_type and f['object_id'] == object_id], template)


@library.global_function
@contextfunction
def render_all_feeds(context, template='feeds/feeds.html'):
	feeds = getattr(context.get('request'), '_feeds', [])
	return render_feed_list(feeds, template)
