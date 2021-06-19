# -*- coding: utf-8 -*-
class FeedsRegister(object):
	standard_feeds = []

	def __init__(self):
		super(FeedsRegister, self).__init__()
		self.dynamic_feeds = []

	@staticmethod
	def prepare_feed(feed, object_type=None, object_id=None):
		return {
			'title': feed.title() if callable(feed.title) else feed.title,
			'url': feed.feed_url() if callable(feed.feed_url) else feed.feed_url,
			'object_type': object_type,
			'object_id': object_id,
		}

	@staticmethod
	def register_standard_feed(feed, object_type=None, object_id=None):
		FeedsRegister.standard_feeds.append(FeedsRegister.prepare_feed(feed, object_type, object_id))

	def register_feed(self, feed, object_type=None, object_id=None):
		self.dynamic_feeds.append(FeedsRegister.prepare_feed(feed, object_type, object_id))

	def __iter__(self):
		for feed in FeedsRegister.standard_feeds:
			yield feed
		for feed in self.dynamic_feeds:
			yield feed


def register_feed(request, feed, object_type=None, object_id=None):
	register = getattr(request, '_feeds')
	register.register_feed(feed, object_type, object_id)
