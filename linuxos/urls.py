# -*- coding: utf-8 -*-
from django.urls import path

from . import redirect_views
from .static_urls import urlpatterns as static_urlpatterns


urlpatterns = [
	path('profil/<int:pk>/index.html', redirect_views.profile_redirect),
	path('clanok/<int:pk>/index.html', redirect_views.article_redirect),
	path('clanok_pdf/<int:pk>/index.html', redirect_views.article_redirect),
	path('clanok.php', redirect_views.article_old_redirect),
	path('users.php', redirect_views.profile_old_redirect),
	path('clanky/kategoria/<int:pk>/index.html', redirect_views.article_category_redirect),
	path('forum/<int:pk>/index.html', redirect_views.forum_topic_redirect),
	path('forum_zoznam/sekcia/<int:category>/index.html', redirect_views.forum_category_redirect),
	path('forum_zoznam/<int:page>/sekcia/<int:category>/index.html', redirect_views.forum_category_redirect),
	path('zobraz_prispevok.php', redirect_views.forum_topic_old_redirect),
	path('sprava_zobraz_komentare/<int:pk>/index.html', redirect_views.news_redirect),
	path('anketa_show/<int:pk>/index.html', redirect_views.poll_redirect),
	path('KnowledgeBase_show_entry/<int:pk>/index.html', redirect_views.wiki_redirect),
	path('KnowledgeBase_show_entry/<int:pk>/history/true/index.html', redirect_views.wiki_redirect),
	path('KnowledgeBase_show_entry/<int:pk>/history/true', redirect_views.wiki_redirect),
	path('spravy_historia/index.html', redirect_views.news_list_redirect),
	path('spravy_historia/<int:page>/index.html', redirect_views.news_list_redirect),
	path('forum_zoznam/index.html', redirect_views.topic_list_redirect),
	path('sprava_pridaj_odpoved/<int:pk>/index.html', redirect_views.news_comment_redirect),
	path('sprava_pridaj_odpoved/<int:pk>/parent/<int:parent>/index.html', redirect_views.comments_redirect),
	path('index.html', redirect_views.home_redirect),
	path('index.php', redirect_views.old_php_redirect),
	path('forum_rss/index.html', redirect_views.forum_rss_redirect),
	path('spravy_rss/index.html', redirect_views.news_rss_redirect),
	path('clanok_rss/index.html', redirect_views.article_rss_redirect),
	path('eshop/kategoria/<int:pk>/index.html', redirect_views.eshop_redirect),
	path('eshop/<int:pk>/kategoria/<int:category>/index.html', redirect_views.eshop_redirect),
	path('eshop_zobraz_tovar/<int:pk>/kategoria/<int:category>/index.html', redirect_views.eshop_redirect),
	path('eshop_zobraz_tovar/<int:pk>/index.html', redirect_views.eshop_redirect),
	path('eshop_pridaj_odpoved/<int:pk>/index.html', redirect_views.eshop_redirect),
	path('autori/', redirect_views.home_temp_redirect),
	path('autori/index.html', redirect_views.home_temp_redirect),
	path('forum/strana/<int:page>/', redirect_views.forum_page_redirect),
	path('spravy/zoznam/<int:page>/', redirect_views.news_page_redirect),
]

urlpatterns += static_urlpatterns
