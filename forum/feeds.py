# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse_lazy
from django.utils.encoding import smart_unicode

from forum.models import Topic, Section


class TopicFeed(Feed):
	title = u"Fórum"
	description = u"Témy fóra"
	link = reverse_lazy('forum:overview')
	feed_url = reverse_lazy('forum:feed-latest')

	def categories(self):
		return Section.objects.values_list('name', flat = True)

	def item_description(self, item):
		return item.text

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
		return [smart_unicode(item.section)]

	def items(self):
		return Topic.topics.all().select_related('author', 'section').order_by('-pk')[:settings.FEED_SIZE]
