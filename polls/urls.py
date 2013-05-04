# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url


class Patterns(object):
	def __init__(self):
		self.app_name = 'polls'
		self.name = 'polls'

	@property
	def urls(self):
		urlpatterns = patterns('polls.views',
			url(r'^$', 'poll_list', name = 'list'),
			url(r'^zoznam/(?P<page>\d+)/', 'poll_list', name = 'list-page'),
			url(r'^post/(?P<pk>\d+)/$', 'post', name = 'post'),
			url(r'^vytvorit/$', 'create', name = 'create'),
			url(r'^detail/(?P<slug>[-\w]+)/$', 'poll_detail_by_slug', name = "detail-by-slug"),
		)
		return (urlpatterns, self.app_name, self.name)

urlpatterns = Patterns().urls
