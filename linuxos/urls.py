# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import redirect_views
from .static_urls import urlpatterns as static_urlpatterns


urlpatterns = [
	url(r'^profil/(?P<pk>\d+)/index.html$', redirect_views.profile_redirect),
	url(r'^clanok/(?P<pk>\d+)/index.html$', redirect_views.article_redirect),
	url(r'^clanok_pdf/(?P<pk>\d+)/index.html$', redirect_views.article_redirect),
	#url(r'^clanok/(?P<pk>\d+)/$', redirect_views.article_redirect), tak toto koliduje so stránkovaním
	url(r'^clanok.php$', redirect_views.article_old_redirect),
	url(r'^users.php$', redirect_views.profile_old_redirect),
	url(r'^clanky/kategoria/(?P<pk>\d+)/index.html$', redirect_views.article_category_redirect),
	url(r'^forum/(?P<pk>\d+)/index.html$', redirect_views.forum_topic_redirect),
	url(r'^forum_zoznam/sekcia/(?P<category>\d+)/index.html$', redirect_views.forum_category_redirect),
	url(r'^forum_zoznam/(?P<page>\d+)/sekcia/(?P<category>\d+)/index.html$', redirect_views.forum_category_redirect),
	url(r'^zobraz_prispevok.php$', redirect_views.forum_topic_old_redirect),
	url(r'^sprava_zobraz_komentare/(?P<pk>\d+)/index.html$', redirect_views.news_redirect),
	url(r'^anketa_show/(?P<pk>\d+)/index.html$', redirect_views.poll_redirect),
	url(r'^KnowledgeBase_show_entry/(?P<pk>\d+)/index.html$', redirect_views.wiki_redirect),
	url(r'^KnowledgeBase_show_entry/(?P<pk>\d+)/history/true/index.html$', redirect_views.wiki_redirect),
	url(r'^KnowledgeBase_show_entry/(?P<pk>\d+)/history/true$', redirect_views.wiki_redirect),
	url(r'^spravy_historia/index.html$', redirect_views.news_list_redirect),
	url(r'^spravy_historia/(?P<page>\d+)/index.html$', redirect_views.news_list_redirect),
	url(r'^forum_zoznam/index.html$', redirect_views.topic_list_redirect),
	url(r'^sprava_pridaj_odpoved/(?P<pk>\d+)/index.html$', redirect_views.news_comment_redirect),
	url(r'^sprava_pridaj_odpoved/\d+/parent/(?P<parent>\d+)/index.html$', redirect_views.comments_redirect),
	url(r'^index.html$', redirect_views.home_redirect),
	url(r'^index.php$', redirect_views.old_php_redirect),
	url(r'^forum_rss/index.html$', redirect_views.forum_rss_redirect),
	url(r'^spravy_rss/index.html$', redirect_views.news_rss_redirect),
	url(r'^clanok_rss/index.html$', redirect_views.article_rss_redirect),
	url(r'^eshop/kategoria/(?P<pk>\d+)/index.html$', redirect_views.eshop_redirect),
	url(r'^eshop/(?P<pk>\d+)/kategoria/(?P<category>\d+)/index.html$', redirect_views.eshop_redirect),
	url(r'^eshop_zobraz_tovar/(?P<pk>\d+)/kategoria/(?P<category>\d+)/index.html$', redirect_views.eshop_redirect),
	url(r'^eshop_zobraz_tovar/(?P<pk>\d+)/index.html$', redirect_views.eshop_redirect),
	url(r'^eshop_pridaj_odpoved/(?P<pk>\d+)/index.html$', redirect_views.eshop_redirect),
	url(r'^autori/(index.html)?$', redirect_views.home_temp_redirect),
	url(r'^forum/strana/(?P<page>\d+)/$', redirect_views.forum_page_redirect),
	url(r'^spravy/zoznam/(?P<page>\d+)/$', redirect_views.news_page_redirect),
]

urlpatterns += static_urlpatterns
