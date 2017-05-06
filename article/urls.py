# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import feeds, views


urlpatterns = [
	url(r'^(?:(?P<page>\d+)/)?$', views.ArticleListView.as_view(), name='list'),
	url(r'^(?P<slug>[-\w]+)/$', views.ArticleDetailView.as_view(), name='detail'),
	url(r'^kategoria/(?P<category>[-\w]+)/(?:(?P<page>\d+)/)?$', views.ArticleListView.as_view(), name='list-category'),
	url(r'^serial/zoznam/(?:(?P<page>\d+)/)?$', views.SeriesListView.as_view(), name='series'),
	url(r'^serial/(?P<category>[-\w]+)/(?:(?P<page>\d+)/)?$', views.ArticleSeriesView.as_view(), name='list-series'),
	url(r'^feeds/latest/$', feeds.LatestArticleFeed(), name='feed-latest'),
]
