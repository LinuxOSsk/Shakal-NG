# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
import views


class Patterns(object):
	def __init__(self):
		self.app_name = 'admin_dashboard'
		self.name = 'admin_dashboard'

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(r'^stats/$', views.stats, name = 'stats'),
		)
		return (urlpatterns, self.app_name, self.name)

urlpatterns = Patterns().urls
