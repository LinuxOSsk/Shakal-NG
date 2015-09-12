# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


class Patterns(object):
	def __init__(self):
		self.app_name = 'news'
		self.name = 'news'

	@property
	def urls(self):
		pat = patterns('news.views',
			url(r'^detail/(?P<slug>[-\w]+)/$', 'NewsDetailView', name="detail-by-slug"),
			url(r'^pridat/$', 'NewsCreateView', name='create'),
			url(r'^(?:(?P<page>\d+)/)?$', 'NewsListView', name='list'),
		) + patterns('news.feeds',
			url(r'^feeds/latest/$', 'NewsFeed', name='feed-latest'),
		)
		return (pat, self.app_name, self.name)

urlpatterns = Patterns().urls
