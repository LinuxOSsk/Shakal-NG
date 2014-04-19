# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import ArticleListView, ArticleDetailView
from .feeds import LatestArticleFeed


class Patterns(object):
	def __init__(self):
		self.app_name = 'article'
		self.name = 'article'

	@property
	def urls(self):
		pat = patterns('',
			url(r'^(?:(?P<page>\d+)/)?$', ArticleListView.as_view(), name = 'article-list'),
			url(r'^(?P<slug>[-\w]+)/$', ArticleDetailView.as_view(), name = "detail-by-slug"),
			url(r'^kategoria/(?P<category>[-\w]+)/(?:(?P<page>\d+)/)?$', ArticleListView.as_view(), name = 'list-category'),
			url(r'^feeds/latest/$', LatestArticleFeed(), name = 'feed-latest'),
		)
		return (pat, self.app_name, self.name)

urlpatterns = Patterns().urls
