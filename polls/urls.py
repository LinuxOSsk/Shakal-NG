# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views as poll_views

class Patterns(object):
	def __init__(self):
		self.app_name = 'polls'
		self.name = 'polls'

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(r'^$', poll_views.poll_list, name = 'list'),
			url(r'^zoznam/(?P<page>\d+)/', poll_views.poll_list, name = 'list-page'),
			url(r'^post/(?P<pk>\d+)/$', poll_views.post, name = 'post'),
			url(r'^vytvorit/$', poll_views.create, name = 'create'),
			url(r'^detail/(?P<slug>[-\w]+)/$', poll_views.poll_detail_by_slug, name = "detail-by-slug"),
		)
		return (urlpatterns, self.app_name, self.name)

urlpatterns = Patterns().urls
