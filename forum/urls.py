# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('forum.views',
	url(r'^prehlad/(?:(?P<page>\d+)/)?$', 'TopicListView', name='overview'),
	url('^pridat/$', 'TopicCreateView', name='create'),
	url(r'^(?P<pk>\d+)/$', 'TopicDetailView', name='topic-detail'),
	url(r'^(?P<category>[-\w]+)/(?:(?P<page>\d+)/)?$', 'TopicListView', name='section'),
) + patterns('forum.feeds',
	url(r'^feeds/latest/$', 'TopicFeed', name='feed-latest'),
)
