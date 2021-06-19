# -*- coding: utf-8 -*-
from django.template.response import TemplateResponse

from .auth_remember_utils import authenticate_user, delete_cookie
from .utils import update_last_visited, update_visited_items


UPDATE_LAST_VIEW_TIME = {
	'article:list': 'article.article',
	'blog:post-list': 'blog.post',
	'forum:overview': 'forum.topic',
	'news:list': 'news.news',
	'tweets:list': 'tweets.tweet',
	'wiki:home': 'wiki.page',
}

UPDATE_VISITED_ITEMS = {
	'article:detail': 'article.article',
	'blog:post-detail': 'blog.post',
	'forum:topic-detail': 'forum.topic',
	'news:detail': 'news.news',
	'tweets:detail': 'tweets.tweet',
	'wiki:page': 'wiki.page',
}


class LastViewedMiddleware(object):
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		response = self.get_response(request)
		if not hasattr(request, 'user'):
			return response
		if request.user.is_authenticated and request.resolver_match:
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
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		if not hasattr(request, 'user') or request.user.is_authenticated:
			return self.get_response(request)
		user = authenticate_user(request)
		delete_auth_remember = user is None
		response = self.get_response(request)
		if not hasattr(request, 'user'):
			return response
		if delete_auth_remember:
			delete_cookie(response)
		return response
