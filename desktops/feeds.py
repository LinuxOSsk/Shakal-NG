# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy

from .models import Desktop


class DesktopFeed(Feed):
	title = "Desktopy"
	description = "Najnovšie desktopy"
	link = reverse_lazy('blog:post-list', kwargs={'page': 1})
	feed_url = reverse_lazy('desktops:feed-latest')
	description_template = 'feeds/description/desktop.html'

	def item_author_name(self, item):
		return item.author

	def item_author_link(self, item):
		return item.author.get_absolute_url()

	def item_pubdate(self, item):
		return item.created

	def items(self):
		return (Desktop.objects
			.select_related('author')
			.order_by('-pk')[:settings.FEED_SIZE])
