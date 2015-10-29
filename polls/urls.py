# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('polls.views',
	url(r'^detail/(?P<slug>[-\w]+)/$', 'PollDetail', name='detail-by-slug'),
	url(r'^(?:(?P<page>\d+)/)?$', 'PollList', name='list'),
	url(r'^post/(?P<pk>\d+)/$', 'PollPost', name='post'),
	url(r'^vytvorit/$', 'PollCreate', name='create'),
)
