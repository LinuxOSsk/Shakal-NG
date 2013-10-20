# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

import blog_feeds
import blog.views as blog_views


class Patterns(object):
	def __init__(self):
		self.app_name = 'blog'
		self.name = 'blog'

	@property
	def urls(self):
		url_patterns = patterns('',
			url(r'^(?:(?P<page>\d+)/)?$', blog_views.PostListView.as_view(), name='post-list'),
			url(r'^admin/edit/$', login_required(blog_views.edit), name='edit'),
			url(r'^admin/my/$', login_required(blog_views.my_blog), name='my'),
			url(r'^admin/create-post/$', login_required(blog_views.PostCreateView.as_view()), name='post_create'),
			url(r'^(?P<category>[\w-]+)/list/(?:(?P<page>\d+)/)?$', blog_views.PostListView.as_view(), name='view'),
			url(r'^(?P<category>[\w-]+)/detail/(?P<slug>[\w-]+)/$', blog_views.PostDetailView.as_view(), name='detail'),
			url(r'^(?P<category>[\w-]+)/update/(?P<slug>[\w-]+)/$', login_required(blog_views.PostUpdateView.as_view()), name='post_edit'),
			url(r'^feeds/latest/$', blog_feeds.PostFeed(), name='post-feed-latest'),
			url(r'^feeds/linux/$', blog_feeds.PostFeed(linux=True), name='feed-linux'),
			url(r'^(?P<blog_slug>[\w-]+)/feed/$', blog_feeds.PostFeed(), name='post-feed-blog'),
		)
		return (url_patterns, self.app_name, self.name)

urlpatterns = Patterns().urls
