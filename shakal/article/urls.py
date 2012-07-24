# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import DetailView
from shakal.article.models import Article

class Patterns(object):
	def __init__(self):
		self.app_name = 'article'
		self.name = 'article'

	@property
	def urls(self):
		urlpatterns = patterns('',
			url(r'^(?P<slug>[-\w]+)/$', DetailView.as_view(model = Article), name = "detail")
		)
		return (urlpatterns, self.app_name, self.name)

urlpatterns = Patterns().urls
