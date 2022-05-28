# -*- coding: utf-8 -*-
import datetime

import feedparser
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django_jinja import library
from jinja2 import pass_context


def render_feed_list(feeds, template):
	return mark_safe(render_to_string(template, {'feeds': feeds}))


@library.global_function
@pass_context
def render_feeds(context, object_type=None, object_id=None, template='feeds/feeds.html'):
	feeds = getattr(context.get('request'), '_feeds', [])
	return render_feed_list([f for f in feeds if f['object_type'] == object_type and f['object_id'] == object_id], template)


@library.global_function
@pass_context
def render_all_feeds(context, template='feeds/feeds.html'):
	feeds = getattr(context.get('request'), '_feeds', [])
	return render_feed_list(feeds, template)


@library.global_function
def pull_feeds(url, max_count=4):
	posts = []
	feed = feedparser.parse(url)
	entries_count = len(feed.entries)
	for i in range(min(max_count, entries_count)):
		try:
			pub_date = feed.entries[i].published_parsed
		except AttributeError:
			pub_date = feed.entries[i].updated_parsed
		published = datetime.date(pub_date[0], pub_date[1], pub_date[2])
		try:
			posts.append({
				'title': feed.entries[i].title,
				'link': feed.entries[i].link,
				'published': published,
			})
		except IndexError:
			pass
	ctx = {'posts': posts}
	return mark_safe(render_to_string("feeds/pull_feeds.html", ctx))
