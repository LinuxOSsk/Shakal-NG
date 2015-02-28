# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


class Patterns(object):
	def __init__(self):
		self.app_name = 'article'
		self.name = 'article'

	@property
	def urls(self):
		pat = patterns('article.views',
			url(r'^(?:(?P<page>\d+)/)?$', 'ArticleListView', name='list'),
			url(r'^(?P<slug>[-\w]+)/$', 'ArticleDetailView', name='detail'),
			url(r'^kategoria/(?P<category>[-\w]+)/(?:(?P<page>\d+)/)?$', 'ArticleListView', name='list-category'),
		) + patterns('article.feeds',
			url(r'^feeds/latest/$', 'LatestArticleFeed', name='feed-latest'),
		)
		return (pat, self.app_name, self.name)

urlpatterns = Patterns().urls
