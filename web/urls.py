# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.contenttypes import views as contenttype_views
from django.urls import include, path, register_converter
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from django_simple_paginator.converter import PageConverter

import template_dynamicloader.views
import web.views


register_converter(PageConverter, 'page')


urlpatterns = [
	path('', web.views.Home.as_view(), name='home'),
	path('', include('linuxos.urls')),
	path(_('login/'), include('allauth.urls')),
	path(_('accounts/'), include('accounts.urls')),
	path(_('article/'), include('article.urls')),
	path(_('blog/'), include('blog.urls')),
	path('blackhole/', include('blackhole.urls')),
	path(_('comments/'), include('comments.urls')),
	path('desktopy/', include('desktops.urls')),
	path(_('forum/'), include('forum.urls')),
	#path(_('^maintenance/'), include('maintenance.urls')),
	path(_('news/'), include('news.urls')),
	path(_('rating/'), include('rating.urls')),
	path(_('tweets/'), include('tweets.urls')),
	path(_('notifications/'), include('notifications.urls')),
	path(_('polls/'), include('polls.urls')),
	path(_('search/'), include('fulltext.urls')),
	path(_('wiki/'), include('wiki.urls')),
	path(_('template-change/'), template_dynamicloader.views.change, name='template-change'),
	path(_('templates/'), template_dynamicloader.views.TemplateListView.as_view(), name='template-list'),
	path('v/<int:content_type_id>/<str:object_id>/', contenttype_views.shortcut, name='view-object'),
	path(_('admin/'), admin.site.urls),
	path(_('admin_dashboard/'), include('admin_dashboard.urls')),
	path('api/editor/', include('rich_editor.urls')),
	path('hijack/', include('hijack.urls')),
	path('django-email-log/', include('django_email_log.urls')),
	path('image/', include('image_renderer.urls')),
	path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'images/favicon/favicon.ico', permanent=True)),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
	handler404 = 'web.views.error_404'
	handler500 = 'web.views.error_500'

if settings.DEBUG:
	try:
		import debug_toolbar
		urlpatterns += [
			path('__debug__/', include(debug_toolbar.urls)),
		]
	except ImportError:
		pass
