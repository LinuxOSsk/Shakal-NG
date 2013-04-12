# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse_lazy

from threaded_comments.models import Comment


class CommentFeed(Feed):
	title = u"Diskusné príspevky"
	description = "Zoznam posledných diskusných príspevkov"
	link = reverse_lazy('home')
	feed_url = reverse_lazy('comments-feed-latest')

	def item_description(self, item):
		return item.comment

	def item_author_name(self, item):
		return item.user_name

	def item_author_link(self, item):
		if item.user:
			return item.user.get_absolute_url()
		else:
			return None

	def item_pubdate(self, item):
		return item.submit_date

	def items(self):
		return Comment.plain_objects.filter(level__gt = 0).select_related('user').order_by('-id')[:settings.FEED_SIZE]
