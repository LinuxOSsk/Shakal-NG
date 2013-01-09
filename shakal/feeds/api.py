# -*- coding: utf-8 -*-

__all__ = ('register_feed', )


def register_feed(request, feed, object_type = None, object_id = None):
	if hasattr(request, '_feeds'):
		feed_data = {
			'title': feed.title,
			'url': feed.feed_url,
			'object_type': object_type,
			'object_id': object_id,
		}
		request._feeds.append(feed_data)
