# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url


urlpatterns = [
	url(r'^$', 'List', name='list'),
	url(r'^r/(?P<pk>\d+)/$', 'Read', name='read'),
]
