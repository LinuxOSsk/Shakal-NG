# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
	'accounts': GenericSitemap({'queryset': User.objects.filter(is_active=True)}, changefreq='monthly', priority=0.2),
	'articles': GenericSitemap({'queryset': Article.objects.all(), 'date_field': 'pub_time'}, priority=0.9),
	'blogposts': GenericSitemap({'queryset': Post.objects.all(), 'date_field': 'updated'}, priority=0.6),
	'blogs': GenericSitemap({'queryset': Blog.objects.all(), 'date_field': 'updated'}, priority=0.8),
	'desktops': GenericSitemap({'queryset': Desktop.objects.all(), 'date_field': 'updated'}, priority=0.5),
	'news': GenericSitemap({'queryset': News.objects.all(), 'date_field': 'updated'}, priority=0.5),
	'topics': GenericSitemap({'queryset': Topic.objects.topics(), 'date_field': 'updated'}, priority=0.5),
	'wiki': GenericSitemap({'queryset': WikiPage.objects.all(), 'date_field': 'updated'}, priority=0.7),
	'blackhole_story': GenericSitemap({'queryset': Node.objects.all().filter(node_type='story'), 'date_field': 'updated'}, priority=0.7),
}
