# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

class Pattenrs(object):
	def __init__(self):
		self.app_name = 'accounts'
		self.name = 'accounts'

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(r'^', include('registration.backends.default.urls')),
		)
		return (urlpatterns, self.app_name, self.name)


urlpatterns = Pattenrs().urls
