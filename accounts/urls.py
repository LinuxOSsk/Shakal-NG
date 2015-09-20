# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


class Patterns(object):
	def __init__(self):
		self.app_name = 'accounts'
		self.name = 'accounts'

	@property
	def urls(self):
		pat = patterns('accounts.views',
			url(r'^$', 'UserZone', name='user_zone'),
			url(r'^(?P<pk>\d+)/$', 'Profile', name='profile'),
			url(r'^(?P<pk>\d+)/prispevky/$', 'UserPosts', name='user_posts'),
			url(r'^(?P<pk>\d+)/prispevky/clanky/(?:(?P<page>\d+)/)?$', 'UserPostsArticle', name='user_posts_article'),
			url(r'^(?P<pk>\d+)/prispevky/blogy/(?:(?P<page>\d+)/)?$', 'UserPostsBlogpost', name='user_posts_blogpost'),
			url(r'^(?P<pk>\d+)/prispevky/spravy/(?:(?P<page>\d+)/)?$', 'UserPostsNews', name='user_posts_news'),
			url(r'^ja/$', 'MyProfile', name='my_profile'),
			url(r'^ja/upravit/$', 'MyProfileEdit', name='my_profile_edit'),
		)
		return (pat, self.app_name, self.name)


urlpatterns = Patterns().urls
