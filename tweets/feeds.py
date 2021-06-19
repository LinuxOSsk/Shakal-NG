# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from django.utils.encoding import force_str

from .models import Tweet


class TweetFeed(Feed):
	title = 'Tweety'
	description = 'Zoznam posledných tweetov'
	link = reverse_lazy('tweets:list', kwargs={'page': 1})
	feed_url = reverse_lazy('tweets:feed-latest')
	description_template = 'feeds/description/tweet.html'

	def item_author_name(self, item):
		return force_str(item.author)

	def item_author_link(self, item):
		return item.author.get_absolute_url()

	def item_pubdate(self, item):
		return item.created

	def items(self):
		return (Tweet.objects
			.prefetch_related('author')
			.order_by('-pk')[:settings.FEED_SIZE])
