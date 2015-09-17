# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


class Patterns(object):
	def __init__(self):
		self.app_name = 'polls'
		self.name = 'polls'

	@property
	def urls(self):
		pat = patterns('polls.views',
			url(r'^detail/(?P<slug>[-\w]+)/$', 'PollDetail', name='detail-by-slug'),
			url(r'^(?:(?P<page>\d+)/)?$', 'PollList', name='list'),
			url(r'^post/(?P<pk>\d+)/$', 'PollPost', name='post'),
			url(r'^vytvorit/$', 'PollCreate', name='create'),
		)
		return (pat, self.app_name, self.name)

urlpatterns = Patterns().urls
