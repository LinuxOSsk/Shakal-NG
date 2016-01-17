# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template.response import TemplateResponse

from .auth_remember_utils import authenticate_user, delete_cookie
from .utils import update_last_visited, update_visited_items


UPDATE_LAST_VIEW_TIME = {
	'article:list': 'article.article',
	'blog:post-list': 'blog.post',
	'forum:overview': 'forum.topic',
	'news:list': 'news.news',
	'wiki:home': 'wiki.page',
}

UPDATE_VISITED_ITEMS = {
	'article:detail': 'article.article',
	'blog:post-detail': 'blog.post',
	'forum:overview': 'forum.topic',
	'news:detail': 'news.news',
	'wiki:page': 'wiki.page',
}


class LastViewedMiddleware(object):
	def process_response(self, request, response):
		if not hasattr(request, 'user'):
			return response
		if request.user.is_authenticated() and request.resolver_match:
			if request.resolver_match.view_name in UPDATE_LAST_VIEW_TIME:
				content_type = UPDATE_LAST_VIEW_TIME[request.resolver_match.view_name]
				if content_type is not None or not request.user.user_settings:
					update_last_visited(request.user, content_type)
			elif request.resolver_match.view_name in UPDATE_VISITED_ITEMS and isinstance(response, TemplateResponse):
				content_type = UPDATE_VISITED_ITEMS[request.resolver_match.view_name]
				if 'object' in response.context_data:
					pk = response.context_data['object'].pk
					update_visited_items(request.user, content_type, pk)
		return response


class AuthRememberMiddleware(object):
	def process_request(self, request):
		if not hasattr(request, 'user') or request.user.is_authenticated():
			return
		user = authenticate_user(request)
		if user is None:
			setattr(request, '_delete_auth_remember', True)

	def process_response(self, request, response):
		if not hasattr(request, 'user'):
			return response
		if getattr(request, '_delete_auth_remember', False):
			delete_cookie(response)
		return response
