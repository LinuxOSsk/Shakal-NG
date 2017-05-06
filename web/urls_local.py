# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.conf.urls import include, url
from web.urls import urlpatterns as original_urls

urlpatterns = []

if settings.DEBUG:
	import debug_toolbar
	urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)),]
else:
	urlpatterns += [
		(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
	]
	urlpatterns += [
		(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))})
	]

urlpatterns += original_urls

if not settings.DEBUG:
	handler404 = 'web.views.error_404'
	handler500 = 'web.views.error_500'

