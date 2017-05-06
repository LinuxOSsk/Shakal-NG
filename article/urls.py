# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url


urlpatterns = [
	url(r'^(?:(?P<page>\d+)/)?$', 'ArticleListView', name='list'),
	url(r'^(?P<slug>[-\w]+)/$', 'ArticleDetailView', name='detail'),
	url(r'^kategoria/(?P<category>[-\w]+)/(?:(?P<page>\d+)/)?$', 'ArticleListView', name='list-category'),
	url(r'^serial/zoznam/(?:(?P<page>\d+)/)?$', 'SeriesListView', name='series'),
	url(r'^serial/(?P<category>[-\w]+)/(?:(?P<page>\d+)/)?$', 'ArticleSeriesView', name='list-series'),
	url(r'^feeds/latest/$', 'LatestArticleFeed', name='feed-latest'),
]
