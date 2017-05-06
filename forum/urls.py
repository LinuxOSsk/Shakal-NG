# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.views.generic.base import RedirectView


urlpatterns = [
	url(r'^$', RedirectView.as_view(pattern_name='forum:overview', permanent=False)),
	url(r'^prehlad/(?:(?P<page>\d+)/)?$', 'TopicListView', name='overview'),
	url(r'^pridat/$', 'TopicCreateView', name='create'),
	url(r'^(?P<pk>\d+)/$', 'TopicDetailView', name='topic-detail'),
	url(r'^(?P<category>[-\w]+)/(?:(?P<page>\d+)/)?$', 'TopicListView', name='section'),
	url(r'^feeds/latest/$', 'TopicFeed', name='feed-latest'),
]
