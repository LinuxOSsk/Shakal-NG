# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


class Patterns(object):
	def __init__(self):
		self.app_name = 'notifications'
		self.name = 'notifications'

	@property
	def urls(self):
		pat = patterns('notifications.views',
			url(r'^$', 'List', name='list'),
			url(r'^r/(?P<pk>\d+)/$', 'Read', name='read'),
		)
		return (pat, self.app_name, self.name)

urlpatterns = Patterns().urls
