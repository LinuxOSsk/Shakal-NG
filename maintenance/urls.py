# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _
from maintenance.views import status

class Pattenrs(object):
	def __init__(self):
		self.app_name = 'maintenance'
		self.name = 'maintenance'

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(_(r'^status/$'), status, name = 'status'),
		)
		return (urlpatterns, self.app_name, self.name)


urlpatterns = Pattenrs().urls
