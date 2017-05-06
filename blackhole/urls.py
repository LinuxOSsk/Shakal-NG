# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url


urlpatterns = [
	url(r'^clanky/(?:(?P<page>\d+)/)?$', 'StoryList', name='story_list'),
	url(r'^clanky/kategoria/(?P<category>\d+)/(?:(?P<page>\d+)/)?$', 'StoryList', name='story_list_term'),
	url(r'^clanok/(?P<pk>\d+)/$', 'StoryDetail', name='story_detail'),
]
