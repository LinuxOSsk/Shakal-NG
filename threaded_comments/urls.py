# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


class Patterns(object):
	def __init__(self):
		self.app_name = 'threaded_comments'
		self.name = 'threaded_comments'

	@property
	def urls(self):
		pat = patterns('threaded_comments.views',
			url(r'^reply/(?P<parent>\d+)/$', 'Reply', name='reply'),
			url(r'^lock/(?P<pk>\d+)/$', 'Admin', name='admin'),
			url(r'^watch/(?P<pk>\d+)/$', 'Watch', name='watch'),
			url(r'^(?P<pk>\d+)/$', 'Comments', name='comments'),
			url(r'^view/(?P<pk>\d+)/$', 'CommentDetailSingle', name='comment-single'),
			url(r'^id/(?P<pk>\d+)/$', 'CommentDetail', name='comment'),
		) + patterns('threaded_comments.feeds',
			url(r'^feeds/latest/$', 'CommentFeed', name='feed-latest'),
		)
		return (pat, self.app_name, self.name)

urlpatterns = Patterns().urls
