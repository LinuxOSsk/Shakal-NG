# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('accounts.views',
	url(r'^$', 'UserZone', name='user_zone'),
	url(r'^(?P<pk>\d+)/$', 'Profile', name='profile'),
	url(r'^(?P<pk>\d+)/prispevky/$', 'UserPosts', name='user_posts'),
	url(r'^(?P<pk>\d+)/prispevky/clanky/(?:(?P<page>\d+)/)?$', 'UserPostsArticle', name='user_posts_article'),
	url(r'^(?P<pk>\d+)/prispevky/blogy/(?:(?P<page>\d+)/)?$', 'UserPostsBlogpost', name='user_posts_blogpost'),
	url(r'^(?P<pk>\d+)/prispevky/spravy/(?:(?P<page>\d+)/)?$', 'UserPostsNews', name='user_posts_news'),
	url(r'^(?P<pk>\d+)/prispevky/forum-temy/(?:(?P<page>\d+)/)?$', 'UserPostsForumTopic', name='user_posts_forumtopic'),
	url(r'^(?P<pk>\d+)/prispevky/komentare/(?:(?P<page>\d+)/)?$', 'UserPostsCommented', name='user_posts_commented'),
	url(r'^(?P<pk>\d+)/prispevky/wiki/(?:(?P<page>\d+)/)?$', 'UserPostsWikiPage', name='user_posts_wikipage'),
	url(r'^ja/$', 'MyProfile', name='my_profile'),
	url(r'^ja/sledovane/$', 'MyWatched', name='my_watched'),
	url(r'^ja/upravit/$', 'MyProfileEdit', name='my_profile_edit'),
)
