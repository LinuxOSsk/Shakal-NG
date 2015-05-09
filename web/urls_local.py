# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.conf.urls import patterns, include, url
from web.urls import urlpatterns as original_urls

urlpatterns = patterns('',
)

if settings.DEBUG:
	import debug_toolbar
	urlpatterns += patterns('', url(r'^__debug__/', include(debug_toolbar.urls)),)
else:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
	)
	urlpatterns += patterns('',
		(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))})
	)

urlpatterns += original_urls

if not settings.DEBUG:
	handler404 = 'web.views.error_404'
	handler500 = 'web.views.error_500'

