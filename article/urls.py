# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

import feeds
import views


class Patterns(object):
	def __init__(self):
		self.app_name = 'article'
		self.name = 'article'

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(r'^(?:(?P<page>\d+)/)?$', views.ArticleListView.as_view(), name = 'article-list'),
			url(r'^(?P<slug>[-\w]+)/$', views.ArticleDetailView.as_view(), name = "detail-by-slug"),
			url(r'^kategoria/(?P<category>[-\w]+)/(?:(?P<page>\d+)/)?$', views.ArticleListView.as_view(), name = 'list-category'),
			url(r'^feeds/latest/$', feeds.LatestArticleFeed(), name = 'feed-latest'),
		)
		return (urlpatterns, self.app_name, self.name)

urlpatterns = Patterns().urls
