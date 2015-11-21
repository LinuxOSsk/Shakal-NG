# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('rich_editor.views',
	url(r'^preview/$', 'Preview', name='preview'),
)
