# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views as survey_views

class Patterns(object):
	def __init__(self):
		self.app_name = 'survey'
		self.name = 'survey'

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(r'^post/(?P<pk>\d+)/$', survey_views.post, name = "post"),
		)
		return (urlpatterns, self.app_name, self.name)

urlpatterns = Patterns().urls
