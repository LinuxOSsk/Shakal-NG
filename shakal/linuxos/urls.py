# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import shakal.linuxos.redirect_views as redirect_views

urlpatterns = patterns('',
	url('^profil/(?P<pk>[0-9]+)/index.html$', redirect_views.profile_redirect),
	url('^clanok/(?P<pk>[0-9]+)/index.html$', redirect_views.article_redirect),
	url('^forum/(?P<pk>[0-9]+)/index.html$', redirect_views.forum_topic_redirect),
)
