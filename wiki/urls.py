# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


class Patterns(object):
	def __init__(self):
		self.app_name='wiki'
		self.name='wiki'

	@property
	def urls(self):
		pat = patterns('wiki.views',
			url(r'^$', 'WikiHomeView', name='home'),
			url(r'(?P<slug>[-\w]+)/create/$', 'PageCreateView', name='create'),
			url(r'(?P<slug>[-\w]+)/edit/$', 'PageUpdateView', name='edit'),
			url(r'(?P<slug>[-\w]+)/history/(?P<history>\d+)/$', 'WikiDetailView', name='page-history'),
			url(r'(?P<slug>[-\w]+)/(?:(?P<page>\d+)/)?$', 'WikiDetailView', name='page'),
		)
		return (pat, self.app_name, self.name)

urlpatterns = Patterns().urls
