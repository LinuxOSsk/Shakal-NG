# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('news.views',
	url(r'^detail/(?P<slug>[-\w]+)/$', 'NewsDetailView', name='detail'),
	url(r'^detail/(?P<slug>[-\w]+)/upravit/$', 'NewsUpdateView', name='update'),
	url(r'^detail/(?P<slug>[-\w]+)/poznamka/$', 'NoteCreate', name='note-create'),
	url(r'^pridat/$', 'NewsCreateView', name='create'),
	url(r'^(?:(?P<page>\d+)/)?$', 'NewsListView', name='list'),
	url(r'^kategoria/(?P<category>[-\w]+)/(?:(?P<page>\d+)/)?$', 'NewsListView', name='list-category'),
) + patterns('news.feeds',
	url(r'^feeds/latest/$', 'NewsFeed', name='feed-latest'),
)
