# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

class Patterns(object):
	def __init__(self):
		self.app_name = 'admin_dashboard'
		self.name = 'admin_dashboard'

	@property
	def urls(self):
		pat = patterns('admin_dashboard.views',
			url(r'^stats/$', 'Stats', name='stats'),
		)
		return (pat, self.app_name, self.name)

urlpatterns = Patterns().urls
