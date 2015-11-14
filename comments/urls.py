# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('comments.views',
	url(r'^reply/(?P<parent>\d+)/$', 'Reply', name='reply'),
	url(r'^lock/(?P<pk>\d+)/$', 'Admin', name='admin'),
	url(r'^watch/(?P<pk>\d+)/$', 'Watch', name='watch'),
	url(r'^(?P<pk>\d+)/$', 'Comments', name='comments'),
	url(r'^view/(?P<pk>\d+)/$', 'CommentDetailSingle', name='comment-single'),
	url(r'^id/(?P<pk>\d+)/$', 'CommentDetail', name='comment'),
) + patterns('comments.feeds',
	url(r'^feeds/latest/$', 'CommentFeed', name='feed-latest'),
)
