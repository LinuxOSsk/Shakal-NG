# -*- coding: utf-8 -*-
from django.apps import AppConfig

from .register import FeedsRegister


class FeedsConfig(AppConfig):
	name = 'feeds'
	verbose_name = 'Feedy'

	def ready(self):
		from article.feeds import ArticleFeed
		from blog.feeds import PostFeed
		from forum.feeds import TopicFeed
		from news.feeds import NewsFeed
		from comments.feeds import CommentFeed
		from desktops.feeds import DesktopFeed
		from tweets.feeds import TweetFeed

		FeedsRegister.register_standard_feed(ArticleFeed())
		FeedsRegister.register_standard_feed(TopicFeed())
		FeedsRegister.register_standard_feed(NewsFeed())
		FeedsRegister.register_standard_feed(PostFeed())
		FeedsRegister.register_standard_feed(CommentFeed())
		FeedsRegister.register_standard_feed(DesktopFeed())
		FeedsRegister.register_standard_feed(TweetFeed())
