# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
import views


class Patterns(object):
	def __init__(self):
		self.app_name = 'notifications'
		self.name = 'notifications'

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(r'^$', views.read, name = 'read'),
		)
		return (urlpatterns, self.app_name, self.name)

urlpatterns = Patterns().urls
