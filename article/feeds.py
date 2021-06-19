# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from django.utils.encoding import force_str

from .models import Article, Category


class ArticleFeed(Feed):
	title = "Články"
	description = "Zoznam najnovších článkov"
	link = reverse_lazy('article:list', kwargs={'page': 1})
	feed_url = reverse_lazy('article:feed-latest')
	description_template = 'feeds/description/article.html'

	def categories(self):
		return Category.objects.values_list('name', flat=True)

	def item_author_name(self, item):
		return item.authors_name

	def item_author_link(self, item):
		if item.author:
			return item.author.get_absolute_url()
		else:
			return None

	def item_pubdate(self, item):
		return item.pub_time

	def item_categories(self, item):
		return [force_str(item.category)]


class LatestArticleFeed(ArticleFeed):
	def items(self):
		return (Article.objects.all()
			.select_related('author', 'category')
			.only('title', 'authors_name', 'pub_time', 'category', 'author', 'filtered_perex')
			.order_by('-pk')[:settings.FEED_SIZE])
