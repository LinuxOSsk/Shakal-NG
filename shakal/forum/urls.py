# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import views as forum_views

class Patterns(object):
	def __init__(self):
		self.app_name = 'forum'
		self.name = 'forum'

	@property
	def urls(self):
		urlpatterns = patterns('',
			url('^(?P<pk>\d+)/$', forum_views.topic_detail, name = 'topic-detail')
		)
		return (urlpatterns, self.app_name, self.name)

urlpatterns = Patterns().urls
