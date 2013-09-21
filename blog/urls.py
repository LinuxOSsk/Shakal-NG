# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

import blog.feeds as blog_feeds
import blog.views as blog_views


class Patterns(object):
	def __init__(self):
		self.app_name = 'blog'
		self.name = 'blog'

	@property
	def urls(self):
		url_patterns = patterns('',
			url(r'^(?:(?P<page>\d+)/)?$', blog_views.BlogListView.as_view(), name = 'list'),
			url(r'^admin/edit/$', blog_views.edit, name = 'edit'),
			url(r'^admin/my/$', blog_views.my_blog, name = 'my'),
			url(r'^(?P<category>[\w-]+)/(?:(?P<page>\d+)/)?$', blog_views.BlogCategoryView.as_view(), name = 'view'),
			#url(r'^feeds/latest/$', blog_feeds.BlogFeed(), name = 'feed-latest'),
			#url(r'^feeds/linux/$', blog_feeds.BlogFeed(linux = True), name = 'feed-linu'),
		)
		return (url_patterns, self.app_name, self.name)

urlpatterns = Patterns().urls
