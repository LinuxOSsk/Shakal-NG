# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views as news_views

class Patterns(object):
	def __init__(self):
		self.app_name = 'news'
		self.name = 'news'

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(r'^detail/(?P<slug>[-\w]+)/$', news_views.news_detail_by_slug, name = "detail-by-slug"),
			url(r'^pridat/$', news_views.NewsCreateView.as_view(), name = 'create'),
		)
		return (urlpatterns, self.app_name, self.name)

urlpatterns = Patterns().urls
