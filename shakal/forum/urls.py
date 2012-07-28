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
			url('^$', forum_views.overview, name = 'overview'),
			url('^pridat/$', forum_views.TopicCreateView.as_view(), name = 'create'),
			url('^strana/(?P<page>\d+)/$', forum_views.overview, name = 'overview-page'),
			url('^(?P<pk>\d+)/$', forum_views.topic_detail, name = 'topic-detail'),
			url('^(?P<section>[-\w]+)/$', forum_views.overview, name = 'section'),
			url('^(?P<section>[-\w]+)/(?P<page>\d+)/$', forum_views.overview, name = 'section-page'),
		)
		return (urlpatterns, self.app_name, self.name)

urlpatterns = Patterns().urls
