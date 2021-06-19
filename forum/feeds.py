# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from django.utils.encoding import force_str

from forum.models import Topic, Section


class TopicFeed(Feed):
	title = "Fórum"
	description = "Témy fóra"
	link = reverse_lazy('forum:overview', kwargs={'page': 1})
	feed_url = reverse_lazy('forum:feed-latest')
	description_template = 'feeds/description/forum_topic.html'

	def categories(self):
		return Section.objects.values_list('name', flat = True)

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
		return [force_str(item.section)]

	def items(self):
		return Topic.topics.all().select_related('author', 'section').order_by('-pk')[:settings.FEED_SIZE]
