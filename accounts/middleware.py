# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .utils import update_last_visited


UPDATE_LAST_VIEW_TIME = {
	'article:list': 'article.article',
	'blog:post-list': 'blog.post',
	'forum:overview': 'forum.topic',
	'news:list': 'news.news',
	'wiki:home': 'wiki.page',
}


class LastViewedMiddleware(object):
	def process_response(self, request, response):
		if request.user.is_authenticated() and request.resolver_match:
			content_type = UPDATE_LAST_VIEW_TIME.get(request.resolver_match.view_name)
			if content_type is not None or not request.user.user_settings:
				update_last_visited(request.user, content_type)
		return response
