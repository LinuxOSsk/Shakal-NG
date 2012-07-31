# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.contrib.comments.urls import urlpatterns as original_urls

urlpatterns = patterns('shakal.threaded_comments.views',
	url(r'^reply/(\d+)/$', 'reply_comment', name = 'comments-reply-comment'),
	url(r'^post/$', 'post_comment', name = 'comments-post-comment'),
	url(r'^posted/$', 'done_comment', name = 'comments-comment-done')
)

urlpatterns += original_urls
