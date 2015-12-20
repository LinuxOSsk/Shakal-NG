# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .auth_remember_utils import authenticate_user, delete_cookie
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
		if not hasattr(request, 'user'):
			return response
		if request.user.is_authenticated() and request.resolver_match:
			content_type = UPDATE_LAST_VIEW_TIME.get(request.resolver_match.view_name)
			if content_type is not None or not request.user.user_settings:
				update_last_visited(request.user, content_type)
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
