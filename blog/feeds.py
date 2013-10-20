# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse_lazy

from blog.models import Post


class PostFeed(Feed):
	title = u"Blogy"
	description = u"Zoznam najnovších blogov"
	link = reverse_lazy('blog:post-list')
	feed_url = reverse_lazy('blog:post-feed-latest')

	def __init__(self, linux=None, *args, **kwargs):
		self.linux_feeds = linux
		super(PostFeed, self).__init__(*args, **kwargs)

	def item_description(self, item):
		return item.perex

	def item_author_name(self, item):
		if item.blog.author:
			return item.blog.author
		else:
			return None

	def item_author_link(self, item):
		if item.blog.author:
			return item.blog.author.get_absolute_url()
		else:
			return None

	def item_pubdate(self, item):
		return item.pub_time

	def items(self):
		objects = Post.objects.select_related('blog', 'blog__author')
		if self.linux_feeds is not None:
			objects = objects.filter(linux = self.linux_feeds)
		return objects[:settings.FEED_SIZE]
