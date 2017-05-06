# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
	url(r'^clanky/(?:(?P<page>\d+)/)?$', views.StoryList.as_view(), name='story_list'),
	url(r'^clanky/kategoria/(?P<category>\d+)/(?:(?P<page>\d+)/)?$', views.StoryList.as_view(), name='story_list_term'),
	url(r'^clanok/(?P<pk>\d+)/$', views.StoryDetail.as_view(), name='story_detail'),
]
