# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns('comments.views',
	url(r'^odpovedat/(?P<parent>\d+)/$', 'Reply', name='reply'),
	url(r'^zamknut/(?P<pk>\d+)/$', 'Admin', name='admin'),
	url(r'^sledovat/(?P<pk>\d+)/$', 'Watch', name='watch'),
	url(r'^zabudnut/(?P<pk>\d+)/$', 'Forget', name='forget'),
	url(r'^pocet/(?P<ctype>\d+)/(?P<pk>\d+)/$', 'CommentCountImage', name='count-image'),
	url(r'^(?P<pk>\d+)/$', 'Comments', name='comments'),
	url(r'^zobrazit/(?P<pk>\d+)/$', 'CommentDetailSingle', name='comment-single'),
	url(r'^id/(?P<pk>\d+)/$', 'CommentDetail', name='comment'),
) + patterns('comments.feeds',
	url(r'^feeds/latest/$', 'CommentFeed', name='feed-latest'),
)
