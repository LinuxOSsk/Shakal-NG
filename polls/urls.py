# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
	url(r'^detail/(?P<slug>[-\w]+)/$', views.PollDetail.as_view(), name='detail-by-slug'),
	url(r'^(?:(?P<page>\d+)/)?$', views.PollList.as_view(), name='list'),
	url(r'^post/(?P<pk>\d+)/$', views.PollPost.as_view(), name='post'),
	url(r'^vytvorit/$', views.PollCreate.as_view(), name='create'),
]
