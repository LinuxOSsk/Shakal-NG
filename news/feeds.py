# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from django.utils.encoding import force_str

from news.models import News, Category


class NewsFeed(Feed):
	title = 'Správy'
	description = 'Zoznam najnovších správ'
	link = reverse_lazy('news:list', kwargs={'page': 1})
	feed_url = reverse_lazy('news:feed-latest')
	description_template = 'feeds/description/news.html'

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
		return item.created

	def item_categories(self, item):
		return [force_str(item.category)]

	def items(self):
		return (News.objects
			.select_related('author', 'category')
			.order_by('-pk')[:settings.FEED_SIZE])
