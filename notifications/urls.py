# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'notifications'

urlpatterns = [
	url(r'^$', views.List.as_view(), name='list'),
	url(r'^r/(?P<pk>\d+)/$', views.Read.as_view(), name='read'),
]
