# -*- coding: utf-8 -*-
from django.contrib import sitemaps
from django.contrib.sitemaps import GenericSitemap
from django.urls import reverse

from accounts.models import User
from article.models import Article
from blackhole.models import Node
from blog.models import Blog, Post
from desktops.models import Desktop
from forum.models import Topic
from linuxos.static_urls import sites
from news.models import News
from tweets.models import Tweet
from wiki.models import Page as WikiPage


class StaticPagesSitemap(sitemaps.Sitemap):
	priority = 1.0
	changefreq = 'monthly'

	def items(self):
		return [s[1] for s in sites]

	def location(self, item):
		return reverse('page_' + item)


sitemaps = {
	'sites': StaticPagesSitemap(),
	'accounts': GenericSitemap({'queryset': User.objects.filter(is_active=True).order_by('-pk')}, changefreq='monthly', priority=0.4),
	'articles': GenericSitemap({'queryset': Article.objects.order_by('-pk'), 'date_field': 'pub_time'}, priority=1.0),
	'blogposts': GenericSitemap({'queryset': Post.objects.order_by('-pk'), 'date_field': 'updated'}, priority=0.7),
	'blogs': GenericSitemap({'queryset': Blog.objects.order_by('-pk'), 'date_field': 'updated'}, priority=0.7),
	'desktops': GenericSitemap({'queryset': Desktop.objects.order_by('-pk'), 'date_field': 'updated'}, priority=0.5),
	'news': GenericSitemap({'queryset': News.objects.order_by('-pk'), 'date_field': 'updated'}, priority=0.5),
	'tweets': GenericSitemap({'queryset': Tweet.objects.order_by('-pk'), 'date_field': 'updated'}, priority=0.4),
	'topics': GenericSitemap({'queryset': Topic.objects.topics().order_by('-pk'), 'date_field': 'updated'}, priority=0.5),
	'wiki': GenericSitemap({'queryset': WikiPage.objects.order_by('-pk'), 'date_field': 'updated'}, priority=0.9),
	'blackhole_story': GenericSitemap({'queryset': Node.objects.order_by('-pk').filter(node_type='story'), 'date_field': 'updated'}, priority=0.8),
}
