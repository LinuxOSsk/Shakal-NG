# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url


urlpatterns = [
	url(r'^admin/update/$', 'BlogUpdateView', name='blog-update'),
	url(r'^(?:(?P<page>\d+)/)?$', 'PostListView', name='post-list'),
	url(r'^admin/create-post/$', 'PostCreateView', name='post-create'),
	url(r'^admin/my/$', 'MyBlogView', name='my'),
	url(r'^(?P<category>[\w-]+)/list/(?:(?P<page>\d+)/)?$', 'PostListView', name='post-list-category'),
	url(r'^(?P<category>[\w-]+)/detail/(?P<slug>[\w-]+)/$', 'PostDetailView', name='post-detail'),
	url(r'^(?P<category>[\w-]+)/update/(?P<slug>[\w-]+)/$', 'PostUpdateView', name='post-update'),
	url(r'^(?P<category>[\w-]+)/update/(?P<slug>[\w-]+)/attachments/$', 'PostAttachmentsUpdateView', name='post-attachments-update'),
	url(r'^feeds/latest/$', 'PostFeed', name='post-feed-latest'),
	url(r'^feeds/linux/$', 'PostFeed', name='post-feed-linux', kwargs={'linux': True}),
	url(r'^(?P<blog_slug>[\w-]+)/feed/$', 'PostFeed', name='post-feed-blog'),
]
