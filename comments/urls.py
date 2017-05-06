# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import feeds, views


urlpatterns = [
	url(r'^odpovedat/(?P<parent>\d+)/$', views.Reply.as_view(), name='reply'),
	url(r'^zamknut/(?P<pk>\d+)/$', views.Admin.as_view(), name='admin'),
	url(r'^sledovat/(?P<pk>\d+)/$', views.Watch.as_view(), name='watch'),
	url(r'^zabudnut/(?P<pk>\d+)/$', views.Forget.as_view(), name='forget'),
	url(r'^pocet/(?P<ctype>\d+)/(?P<pk>\d+)/$', views.CommentCountImage.as_view(), name='count-image'),
	url(r'^(?P<pk>\d+)/$', views.Comments.as_view(), name='comments'),
	url(r'^zobrazit/(?P<pk>\d+)/$', views.CommentDetailSingle.as_view(), name='comment-single'),
	url(r'^id/(?P<pk>\d+)/$', views.CommentDetail.as_view(), name='comment'),
	url(r'^feeds/latest/$', feeds.CommentFeed(), name='feed-latest'),
]
