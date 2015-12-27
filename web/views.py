# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

from django.http import HttpResponseServerError, HttpResponseNotFound
from django.template.loader import get_template
from django.views.generic import TemplateView

from article.models import Article, Category
from blog.models import Post
from common_utils.cache import cached_method
from desktops.models import Desktop
from forum.models import Topic as ForumTopic
from linuxos.templatetags.linuxos import now


def error_500(request):
	template = get_template('500.html')
	except_type, value, _ = sys.exc_info()
	return HttpResponseServerError(template.render({
		'date_now': now(r"Y-m-d\TH:m:sO"),
		'exception_type': except_type.__name__,
		'exception_value': value,
		'request': request
	}))


def error_404(request):
	template = get_template('404.html')
	return HttpResponseNotFound(template.render({
		'date_now': now(r"Y-m-d\TH:m:sO"),
		'request': request,
	}))


class Home(TemplateView):
	template_name = 'home.html'

	@cached_method(tag='article.article')
	def get_articles(self):
		DEFER = ('original_content', 'filtered_content', 'original_annotation', 'filtered_annotation')
		try:
			top_articles = (Article.objects.all()
				.defer(*DEFER)
				.filter(top=True))
			articles = (Article.objects.all()
				.defer(*DEFER)
				.exclude(pk=top_articles[0].pk))
		except IndexError:
			top_articles = Article.objects.all().none()
			articles = (Article.objects.all()
				.defer(*DEFER))

		articles = list(articles.select_related('author', 'category')[:5])
		top_articles = list(top_articles.select_related('author', 'category')[:1])
		return articles, top_articles

	@cached_method(tag='blog.post')
	def get_posts(self):
		try:
			top_posts = list(Post.objects.all().filter(linux=True)[:1])
			posts = Post.objects.all().exclude(pk=top_posts[0].pk)
		except IndexError:
			top_posts = Post.objects.all().none()
			posts = Post.objects.all()
		return list(posts[:4]), top_posts

	@cached_method(tag='forum.topic')
	def get_topics(self):
		forum_new = list(ForumTopic.topics.newest_comments()[:20])
		forum_no_comments = list(ForumTopic.topics.no_comments()[:5])
		forum_most_comments = list(ForumTopic.topics.most_commented()[:5])
		return forum_new, forum_no_comments, forum_most_comments

	@cached_method(tag='desktops.desktop')
	def get_desktops(self):
		return list(Desktop.objects.select_related('author').order_by('-pk')[:4])

	def get_context_data(self, **kwargs):
		ctx = super(Home, self).get_context_data(**kwargs)
		articles, top_articles = self.get_articles()
		posts, top_posts = self.get_posts()
		forum_new, forum_no_comments, forum_most_comments = self.get_topics()

		new_items = []
		for article in top_articles:
			new_items.append(article)
			break
		for article in articles:
			new_items.append(article)
			break
		for i, post in enumerate(posts):
			new_items.append(post)
			if i == 1:
				break
		new_items.sort(key=lambda x: x.created, reverse=True)

		ctx.update({
			'top_articles': top_articles,
			'articles': articles,
			'top_posts': top_posts,
			'posts': posts,
			'forum_new': forum_new,
			'forum_no_comments': forum_no_comments,
			'forum_most_comments': forum_most_comments,
			'new_items': new_items,
			'article_categories': Category.objects.all(),
			'desktops': self.get_desktops()
		})
		return ctx
