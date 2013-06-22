# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

import feeds as blog_feeds
import views as blog_views


class Patterns(object):
	def __init__(self):
		self.app_name = 'blog'
		self.name = 'blog'

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(r'^(?:(?P<page>\d+)/)?$', blog_views.BlogListView.as_view(), name = 'list'),
			#url(r'^feeds/latest/$', blog_feeds.BlogFeed(), name = 'feed-latest'),
			#url(r'^feeds/linux/$', blog_feeds.BlogFeed(linux = True), name = 'feed-linu'),
		)
		return (urlpatterns, self.app_name, self.name)

urlpatterns = Patterns().urls
