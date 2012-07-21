# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib.comments.urls import urlpatterns as original_urls

urlpatterns = patterns('',
	url(r'^', include('registration.backends.default.urls')),
)

urlpatterns += original_urls
