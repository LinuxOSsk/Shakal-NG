# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'wiki'

urlpatterns = [
	url(r'^$', views.WikiHomeView.as_view(), name='home'),
	url(r'(?P<slug>[-\w]+)/create/$', views.PageCreateView.as_view(), name='create'),
	url(r'(?P<slug>[-\w]+)/edit/$', views.PageUpdateView.as_view(), name='edit'),
	url(r'(?P<slug>[-\w]+)/history/(?P<history>\d+)/$', views.WikiDetailView.as_view(), name='page-history'),
	url(r'(?P<slug>[-\w]+)/(?:(?P<page>\d+)/)?$', views.WikiDetailView.as_view(), name='page'),
]
