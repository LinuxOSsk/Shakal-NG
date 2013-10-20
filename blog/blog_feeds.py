# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse_lazy

from blog.models import Blog, Post


class PostFeed(Feed):
	description = u"Zoznam najnovších blogov"
	link = reverse_lazy('blog:post-list')

	def __init__(self, linux=None, blog_slug=None, *args, **kwargs):
		self.linux_feeds = linux
		self.blog_slug = blog_slug
		super(PostFeed, self).__init__(*args, **kwargs)

	def title(self):
		if self.blog_slug is None:
			return u"Blogy"
		else:
			return Blog.objects.get(slug=self.blog_slug).title

	def feed_url(self):
		if self.blog_slug is None:
			return reverse_lazy('blog:post-feed-latest')
		else:
			return reverse_lazy('blog:post-feed-blog', kwargs={'blog_slug': self.blog_slug})

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
			objects = objects.filter(linux=self.linux_feeds)
		if self.blog_slug is not None:
			objects = objects.filter(blog__slug=self.blog_slug)
		return objects[:settings.FEED_SIZE]
