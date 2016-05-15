# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('blackhole.views',
	url(r'^clanky/(?:(?P<page>\d+)/)?$', 'StoryList', name='story_list'),
	url(r'^clanok/(?P<pk>\d+)/$', 'StoryDetail', name='story_detail'),
)
