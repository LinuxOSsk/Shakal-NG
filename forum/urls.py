# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

import feeds as forum_feeds
import views as forum_views


class Patterns(object):
	def __init__(self):
		self.app_name = 'forum'
		self.name = 'forum'

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(r'^prehlad/(?:(?P<page>\d+)/)?$', forum_views.TopicListView.as_view(), name = 'overview'),
			url('^pridat/$', forum_views.TopicCreateView.as_view(), name = 'create'),
			url('^(?P<pk>\d+)/$', forum_views.TopicDetailView.as_view(), name = 'topic-detail'),
			url(r'^(?P<category>[-\w]+)/(?:(?P<page>\d+)/)?$', forum_views.TopicListView.as_view(), name = 'section'),
			url(r'^feeds/latest/$', forum_feeds.TopicFeed(), name = 'feed-latest'),
		)
		return (urlpatterns, self.app_name, self.name)

urlpatterns = Patterns().urls
