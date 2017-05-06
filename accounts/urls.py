# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
	url(r'^$', views.UserZone.as_view(), name='user_zone'),
	url(r'^(?P<pk>\d+)/$', views.Profile.as_view(), name='profile'),
	url(r'^(?P<pk>\d+)/prispevky/$', views.UserPosts.as_view(), name='user_posts'),
	url(r'^(?P<pk>\d+)/prispevky/clanky/(?:(?P<page>\d+)/)?$', views.UserPostsArticle.as_view(), name='user_posts_article'),
	url(r'^(?P<pk>\d+)/prispevky/blogy/(?:(?P<page>\d+)/)?$', views.UserPostsBlogpost.as_view(), name='user_posts_blogpost'),
	url(r'^(?P<pk>\d+)/prispevky/spravy/(?:(?P<page>\d+)/)?$', views.UserPostsNews.as_view(), name='user_posts_news'),
	url(r'^(?P<pk>\d+)/prispevky/forum-temy/(?:(?P<page>\d+)/)?$', views.UserPostsForumTopic.as_view(), name='user_posts_forumtopic'),
	url(r'^(?P<pk>\d+)/prispevky/komentare/(?:(?P<page>\d+)/)?$', views.UserPostsCommented.as_view(), name='user_posts_commented'),
	url(r'^(?P<pk>\d+)/prispevky/wiki/(?:(?P<page>\d+)/)?$', views.UserPostsWikiPage.as_view(), name='user_posts_wikipage'),
	url(r'^(?P<pk>\d+)/mapa/$', views.UserMap.as_view(), name='user_map'),
	url(r'^ja/$', views.MyProfile.as_view(), name='my_profile'),
	url(r'^ja/sledovane/(?:(?P<page>\d+)/)?$', views.MyWatched.as_view(), name='my_watched'),
	url(r'^ja/navstivene/(?:(?P<page>\d+)/)?$', views.MyViewed.as_view(), name='my_viewed'),
	url(r'^ja/upravit/$', views.MyProfileEdit.as_view(), name='my_profile_edit'),
	url(r'^ja/avatar/$', views.MyProfileAvatarEdit.as_view(), name='my_profile_avatar_edit'),
	url(r'^ja/pozicia/$', views.MyProfilePositionEdit.as_view(), name='my_profile_position_edit'),
	url(r'^mapa-uzivatelov/$', views.UsersMap.as_view(), name='users_map'),
]
