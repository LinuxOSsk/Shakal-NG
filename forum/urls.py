# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


class Patterns(object):
	def __init__(self):
		self.app_name = 'forum'
		self.name = 'forum'

	@property
	def urls(self):
		pat = patterns('forum.views',
			url(r'^prehlad/(?:(?P<page>\d+)/)?$', 'TopicListView', name='overview'),
			url('^pridat/$', 'TopicCreateView', name='create'),
			url(r'^(?P<pk>\d+)/$', 'TopicDetailView', name='topic-detail'),
			url(r'^(?P<category>[-\w]+)/(?:(?P<page>\d+)/)?$', 'TopicListView', name='section'),
			url(r'^feeds/latest/$', 'TopicFeed', name='feed-latest'),
		)
		return (pat, self.app_name, self.name)

urlpatterns = Patterns().urls
