# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from article.feeds import ArticleFeed
from blog.blog_feeds import PostFeed
from feeds import register_feed
from forum.feeds import TopicFeed
from news.feeds import NewsFeed
from threaded_comments.feeds import CommentFeed


class FeedsMiddleware(object):
	def process_request(self, request):
		setattr(request, '_feeds', [])
		register_feed(request, ArticleFeed())
		register_feed(request, TopicFeed())
		register_feed(request, NewsFeed())
		register_feed(request, PostFeed())
		register_feed(request, CommentFeed())
