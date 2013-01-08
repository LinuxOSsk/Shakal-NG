# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import feeds as article_feeds
import views as article_views

class Patterns(object):
	def __init__(self):
		self.app_name = 'article'
		self.name = 'article'

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(r'^$', article_views.article_list, name = 'article-list'),
			url(r'^(?P<page>\d+)/$', article_views.article_list, name = 'article-list-page'),
			url(r'^(?P<slug>[-\w]+)/$', article_views.article_detail_by_slug, name = "detail-by-slug"),
			url(r'^kategoria/(?P<category>[-\w]+)/$', article_views.article_list, name = 'list-category'),
			url(r'^kategoria/(?P<category>[-\w]+)/(?P<page>\d+)/$', article_views.article_list, name = 'list-category-page'),
			url(r'^feeds/latest/$', article_feeds.LatestArticleFeed(), name = 'feed-latest'),
		)
		return (urlpatterns, self.app_name, self.name)

urlpatterns = Patterns().urls
