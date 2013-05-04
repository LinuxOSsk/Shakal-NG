# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
import linuxos.redirect_views as redirect_views

urlpatterns = patterns('',
	url('^profil/(?P<pk>\d+)/index.html$', redirect_views.profile_redirect),
	url('^clanok/(?P<pk>\d+)/index.html$', redirect_views.article_redirect),
	url('^forum/(?P<pk>\d+)/index.html$', redirect_views.forum_topic_redirect),
	url('^zobraz_prispevok.php$', redirect_views.forum_topic_old_redirect),
	url('^sprava_zobraz_komentare/(?P<pk>\d+)/index.html', redirect_views.news_redirect),
	url('^anketa_show/(?P<pk>\d+)/index.html', redirect_views.poll_redirect),
	url('^KnowledgeBase_show_entry/(?P<pk>\d+)/index.html', redirect_views.wiki_redirect),
	url('^forum_rss/index.html', redirect_views.forum_rss_redirect),
	url('^spravy_rss/index.html', redirect_views.news_rss_redirect),
	url('^clanok_rss/index.html', redirect_views.article_rss_redirect),
)
