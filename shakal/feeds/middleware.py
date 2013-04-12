# -*- coding: utf-8 -*-
#
from article.feeds import ArticleFeed
from shakal.feeds import register_feed
from shakal.forum.feeds import TopicFeed
from shakal.news.feeds import NewsFeed
from threaded_comments.feeds import CommentFeed


class FeedsMiddleware(object):
	def process_request(self, request):
		setattr(request, '_feeds', [])
		register_feed(request, ArticleFeed)
		register_feed(request, TopicFeed)
		register_feed(request, NewsFeed)
		register_feed(request, CommentFeed)
