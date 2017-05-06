# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import feeds, views


urlpatterns = [
	url(r'^$', RedirectView.as_view(pattern_name='forum:overview', permanent=False)),
	url(r'^prehlad/(?:(?P<page>\d+)/)?$', views.TopicListView.as_view(), name='overview'),
	url(r'^pridat/$', views.TopicCreateView.as_view(), name='create'),
	url(r'^(?P<pk>\d+)/$', views.TopicDetailView.as_view(), name='topic-detail'),
	url(r'^(?P<category>[-\w]+)/(?:(?P<page>\d+)/)?$', views.TopicListView.as_view(), name='section'),
	url(r'^feeds/latest/$', feeds.TopicFeed(), name='feed-latest'),
]
