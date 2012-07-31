# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import shakal.linuxos.redirect_views as redirect_views

urlpatterns = patterns('',
	url('^profil/(?P<pk>\d+)/index.html$', redirect_views.profile_redirect),
	url('^clanok/(?P<pk>\d+)/index.html$', redirect_views.article_redirect),
	url('^forum/(?P<pk>\d+)/index.html$', redirect_views.forum_topic_redirect),
	url('^sprava_zobraz_komentare/(?P<pk>\d+)/index.html', redirect_views.news_redirect),
	url('^anketa_show/(?P<pk>\d+)/index.html', redirect_views.survey_redirect),
)
