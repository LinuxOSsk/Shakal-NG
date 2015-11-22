# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone


UPDATE_LAST_VIEW_TIME = {
	'article:list': 'article.article',
	'blog:post-list': 'blog.post',
	'forum:overview': 'forum.topic',
	'news:list': 'news.news',
	'wiki:home': 'wiki.page',
}


class LastViewedMiddleware(object):
	def process_response(self, request, response):
		if request.user.is_authenticated:
			content_type = UPDATE_LAST_VIEW_TIME.get(request.resolver_match.view_name)
			if content_type is not None or not request.user.user_settings:
				self.update_last_visited(request.user, content_type)
		return response

	def update_last_visited(self, user, content_type):
		now = timezone.now()
		user_settings = user.user_settings
		user_settings.setdefault('last_visited', {})
		last_visited = user_settings['last_visited']
		if content_type:
			last_visited[content_type] = now
		for content_type in UPDATE_LAST_VIEW_TIME.values():
			last_visited.setdefault(content_type, now)
		user.user_settings = user_settings
		user.save()
