# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('admin_dashboard.views',
	url(r'^stats/$', 'Stats', name='stats'),
)
