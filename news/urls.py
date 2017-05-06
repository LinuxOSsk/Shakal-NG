# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import feeds, views


urlpatterns = [
	url(r'^detail/(?P<slug>[-\w]+)/$', views.NewsDetailView.as_view(), name='detail'),
	url(r'^detail/(?P<slug>[-\w]+)/upravit/$', views.NewsUpdateView.as_view(), name='update'),
	url(r'^detail/(?P<slug>[-\w]+)/poznamka/$', views.NoteCreate.as_view(), name='note-create'),
	url(r'^pridat/$', views.NewsCreateView.as_view(), name='create'),
	url(r'^(?:(?P<page>\d+)/)?$', views.NewsListView.as_view(), name='list'),
	url(r'^kategoria/(?P<category>[-\w]+)/(?:(?P<page>\d+)/)?$', views.NewsListView.as_view(), name='list-category'),
	url(r'^feeds/latest/$', feeds.NewsFeed(), name='feed-latest'),
]
