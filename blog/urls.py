# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import feeds, views


urlpatterns = [
	url(r'^admin/update/$', views.BlogUpdateView.as_view(), name='blog-update'),
	url(r'^(?:(?P<page>\d+)/)?$', views.PostListView.as_view(), name='post-list'),
	url(r'^admin/create-post/$', views.PostCreateView.as_view(), name='post-create'),
	url(r'^admin/my/$', views.MyBlogView.as_view(), name='my'),
	url(r'^(?P<category>[\w-]+)/list/(?:(?P<page>\d+)/)?$', views.PostListView.as_view(), name='post-list-category'),
	url(r'^(?P<category>[\w-]+)/detail/(?P<slug>[\w-]+)/$', views.PostDetailView.as_view(), name='post-detail'),
	url(r'^(?P<category>[\w-]+)/update/(?P<slug>[\w-]+)/$', views.PostUpdateView.as_view(), name='post-update'),
	url(r'^(?P<category>[\w-]+)/update/(?P<slug>[\w-]+)/attachments/$', views.PostAttachmentsUpdateView.as_view(), name='post-attachments-update'),
	url(r'^feeds/latest/$', feeds.PostFeed(), name='post-feed-latest'),
	url(r'^feeds/linux/$', feeds.PostFeed(linux=True), name='post-feed-linux'),
	url(r'^(?P<blog_slug>[\w-]+)/feed/$', feeds.PostFeed(), name='post-feed-blog'),
]
