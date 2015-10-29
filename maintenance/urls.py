# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('maintenance.views',
	url(r'^stav/$', 'status', name='status'),
)
