# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from .static_urls import urlpatterns as static_urlpatterns


urlpatterns = [
	url(r'^profil/(?P<pk>\d+)/index.html$', 'profile_redirect'),
	url(r'^clanok/(?P<pk>\d+)/index.html$', 'article_redirect'),
	url(r'^clanok_pdf/(?P<pk>\d+)/index.html$', 'article_redirect'),
	#url(r'^clanok/(?P<pk>\d+)/$', 'article_redirect'), tak toto koliduje so stránkovaním
	url(r'^clanok.php$', 'article_old_redirect'),
	url(r'^users.php$', 'profile_old_redirect'),
	url(r'^clanky/kategoria/(?P<pk>\d+)/index.html$', 'article_category_redirect'),
	url(r'^forum/(?P<pk>\d+)/index.html$', 'forum_topic_redirect'),
	url(r'^forum_zoznam/sekcia/(?P<category>\d+)/index.html$', 'forum_category_redirect'),
	url(r'^forum_zoznam/(?P<page>\d+)/sekcia/(?P<category>\d+)/index.html$', 'forum_category_redirect'),
	url(r'^zobraz_prispevok.php$', 'forum_topic_old_redirect'),
	url(r'^sprava_zobraz_komentare/(?P<pk>\d+)/index.html$', 'news_redirect'),
	url(r'^anketa_show/(?P<pk>\d+)/index.html$', 'poll_redirect'),
	url(r'^KnowledgeBase_show_entry/(?P<pk>\d+)/index.html$', 'wiki_redirect'),
	url(r'^KnowledgeBase_show_entry/(?P<pk>\d+)/history/true/index.html$', 'wiki_redirect'),
	url(r'^KnowledgeBase_show_entry/(?P<pk>\d+)/history/true$', 'wiki_redirect'),
	url(r'^spravy_historia/index.html$', 'news_list_redirect'),
	url(r'^spravy_historia/(?P<page>\d+)/index.html$', 'news_list_redirect'),
	url(r'^forum_zoznam/index.html$', 'topic_list_redirect'),
	url(r'^sprava_pridaj_odpoved/(?P<pk>\d+)/index.html$', 'news_comment_redirect'),
	url(r'^sprava_pridaj_odpoved/\d+/parent/(?P<parent>\d+)/index.html$', 'comments_redirect'),
	url(r'^index.html$', 'home_redirect'),
	url(r'^index.php$', 'old_php_redirect'),
	url(r'^forum_rss/index.html$', 'forum_rss_redirect'),
	url(r'^spravy_rss/index.html$', 'news_rss_redirect'),
	url(r'^clanok_rss/index.html$', 'article_rss_redirect'),
	url(r'^eshop/kategoria/(?P<pk>\d+)/index.html$', 'eshop_redirect'),
	url(r'^eshop/(?P<pk>\d+)/kategoria/(?P<category>\d+)/index.html$', 'eshop_redirect'),
	url(r'^eshop_zobraz_tovar/(?P<pk>\d+)/kategoria/(?P<category>\d+)/index.html$', 'eshop_redirect'),
	url(r'^eshop_zobraz_tovar/(?P<pk>\d+)/index.html$', 'eshop_redirect'),
	url(r'^eshop_pridaj_odpoved/(?P<pk>\d+)/index.html$', 'eshop_redirect'),
	url(r'^autori/(index.html)?$', 'home_temp_redirect'),
	url(r'^forum/strana/(?P<page>\d+)/$', 'forum_page_redirect'),
	url(r'^spravy/zoznam/(?P<page>\d+)/$', 'news_page_redirect'),
]

urlpatterns += static_urlpatterns
