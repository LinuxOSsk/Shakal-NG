# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse_lazy

from news.models import News


class NewsFeed(Feed):
	title = u"Správy"
	description = u"Zoznam najnovších správ"
	link = reverse_lazy('news:list')
	feed_url = reverse_lazy('news:feed-latest')

	def item_description(self, item):
		return item.long_text

	def item_author_name(self, item):
		return item.authors_name

	def item_author_link(self, item):
		if item.author:
			return item.author.get_absolute_url()
		else:
			return None

	def item_pubdate(self, item):
		return item.created

	def items(self):
		return News.objects \
			.select_related('author') \
			.order_by('-pk')[:settings.FEED_SIZE]
