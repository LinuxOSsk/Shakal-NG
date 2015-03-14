# -*- coding: utf-8 -*-
from __future__ import unicode_literals


__all__ = ('register_feed', )


def register_feed(request, feed, object_type = None, object_id = None):
	if hasattr(request, '_feeds'):
		feed_data = {
			'title': feed.title() if callable(feed.title) else feed.title,
			'url': feed.feed_url() if callable(feed.feed_url) else feed.feed_url,
			'object_type': object_type,
			'object_id': object_id,
		}
		getattr(request, '_feeds').append(feed_data)
