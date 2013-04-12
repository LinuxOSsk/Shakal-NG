# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.contrib.comments.urls import urlpatterns as original_urls
from threaded_comments import feeds as threaded_comments_feeds

urlpatterns = patterns('threaded_comments.views',
	url(r'^reply/(\d+)/$', 'reply_comment', name = 'comments-reply-comment'),
	url(r'^post/$', 'post_comment', name = 'comments-post-comment'),
	url(r'^posted/$', 'done_comment', name = 'comments-comment-done'),
	url(r'^lock/(\d+)/$', 'admin', name = 'comments-admin'),
	url(r'^watch/(\d+)/$', 'watch', name = 'comments-watch'),
	url(r'^view/(\d+)/$', 'comment', {'single': True}, name = 'comment-single'),
	url(r'^id/(\d+)/$', 'comment', {'single': False}, name = 'comment'),
	url(r'^(\d+)/$', 'comments', name = 'comments'),
	url(r'^feeds/latest/$', threaded_comments_feeds.CommentFeed(), name = 'comments-feed-latest'),
)

urlpatterns += original_urls
