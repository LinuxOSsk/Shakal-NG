# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.contenttypes import views as contenttype_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView

import search.views
import template_dynamicloader.views
import web.views


urlpatterns = [
	url(r'^$', web.views.Home.as_view(), name='home'),
	url(r'^', include('linuxos.urls')),
	url(_(r'^login/'), include('allauth.urls')),
	url(_(r'^accounts/'), include('accounts.urls')),
	url(_(r'^article/'), include('article.urls')),
	url(_(r'^blog/'), include('blog.urls')),
	url(r'^blackhole/', include('blackhole.urls')),
	url(_(r'^comments/'), include('comments.urls')),
	url(r'^desktopy/', include('desktops.urls')),
	url(_(r'^forum/'), include('forum.urls')),
	#url(_(r'^maintenance/'), include('maintenance.urls')),
	url(_(r'^news/'), include('news.urls')),
	url(_(r'^notifications/'), include('notifications.urls')),
	url(_(r'^polls/'), include('polls.urls')),
	url(_(r'^wiki/'), include('wiki.urls')),
	url(_(r'^template-change/$'), template_dynamicloader.views.change, name='template-change'),
	url(_(r'^search/'), search.views.SearchView(), name='haystack_search'),
	url(r'^v/(?P<content_type_id>\d+)/(?P<object_id>.+)/$', contenttype_views.shortcut, name='view-object'),
	url(_(r'^admin/'), include(admin.site.urls)),
	url(_(r'^admin_dashboard/'), include('admin_dashboard.urls')),
	url(r'^api/editor/', include('rich_editor.urls')),
	url(r'^hijack/', include('hijack.urls')),
	url(r'^django-email-log/', include('django_email_log.urls')),
	url(r'^favicon.ico$', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'), permanent=True)),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
	handler404 = 'web.views.error_404'
	handler500 = 'web.views.error_500'
