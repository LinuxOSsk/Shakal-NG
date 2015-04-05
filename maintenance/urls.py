# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


class Pattenrs(object):
	def __init__(self):
		self.app_name = 'maintenance'
		self.name = 'maintenance'

	@property
	def urls(self):
		pat = patterns('maintenance.views',
			url(r'^stav/$', 'status', name='status'),
		)
		return (pat, self.app_name, self.name)


urlpatterns = Pattenrs().urls
