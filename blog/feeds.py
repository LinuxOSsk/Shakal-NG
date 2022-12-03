# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from .models import Blog, Post


class PostFeed(Feed):
	description = "Zoznam najnovších blogov"
	link = reverse_lazy('blog:post-list', kwargs={'page': 1})
	description_template = 'feeds/description/blog_post.html'

	def __init__(self, linux=None, blog_slug=None, *args, **kwargs):
		self.linux_feeds = linux
		self.blog_slug = blog_slug
		self.blog_title = "Blogy"
		super(PostFeed, self).__init__(*args, **kwargs)

	def __call__(self, request, *args, **kwargs):
		self.blog_slug = kwargs.get('blog_slug')
		if self.blog_slug is not None:
			self.blog_title = get_object_or_404(Blog, slug=self.blog_slug).title
		return super().__call__(request, *args, **kwargs)

	def title(self):
		return self.blog_title

	def feed_url(self):
		if self.blog_slug is None:
			return reverse_lazy('blog:post-feed-latest')
		else:
			return reverse_lazy('blog:post-feed-blog', kwargs={'blog_slug': self.blog_slug})

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
		objects = Post.objects.all().select_related('blog', 'blog__author')
		if self.linux_feeds is not None:
			objects = objects.filter(linux=self.linux_feeds)
		if self.blog_slug is not None:
			objects = objects.filter(blog__slug=self.blog_slug)
		return objects[:settings.FEED_SIZE]
