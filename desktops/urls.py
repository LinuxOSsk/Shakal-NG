# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import feeds, views


app_name = 'desktops'

urlpatterns = [
	url(r'^sprava/vytvorit/$', views.DesktopCreate.as_view(), name='create'),
	url(r'^zoznam/(?:(?P<page>\d+)/)?$', views.DesktopList.as_view(), name='list'),
	url(r'^zoznam/autor/(?P<category>\d+)/(?:(?P<page>\d+)/)?$', views.DesktopList.as_view(), name='list-author'),
	url(r'^detail/(?P<pk>\d+)/$', views.DesktopDetail.as_view(), name='detail'),
	url(r'^upravit/(?P<pk>\d+)/$', views.DesktopUpdate.as_view(), name='update'),
	url(r'^feeds/latest/$', feeds.DesktopFeed(), name='feed-latest'),
]
