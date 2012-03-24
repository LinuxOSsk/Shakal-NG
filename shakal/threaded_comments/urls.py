from django.conf.urls.defaults import patterns, include, url
from django.contrib.comments.urls import urlpatterns as original_urls

urlpatterns = patterns('shakal.threaded_comments.views',
	url(r'^reply/(\d+)/$', 'new_comment', name = 'reply-comment'),
	url(r'^post/$', 'post_comment', name = 'post-comment'),
	url(r'^done/$', 'done_comment', name = 'done-comment'),
)

urlpatterns += original_urls

