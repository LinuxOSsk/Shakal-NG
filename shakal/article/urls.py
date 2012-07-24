# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views as article_views

class Patterns(object):
	def __init__(self):
		self.app_name = 'article'
		self.name = 'article'

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(r'^(?P<slug>[-\w]+)/$', article_views.article_detail_by_slug, name = "detail-by-slug")
		)
		return (urlpatterns, self.app_name, self.name)

urlpatterns = Patterns().urls
