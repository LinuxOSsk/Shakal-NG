# -*- coding: utf-8 -*-
import sys

from django.http import HttpResponseServerError, HttpResponseNotFound
from django.http.response import Http404
from django.template.loader import get_template
from django.urls.exceptions import Resolver404
from django.views.generic import TemplateView

from article.models import Article, Category
from blog.models import Post
from common_utils.cache import cached_method
from desktops.models import Desktop
from forum.models import Topic as ForumTopic
from linuxos.templatetags.linuxos import now
from tweets.models import Tweet


def error_500(request, template_name='500.html'):
	template = get_template(template_name)
	except_type, value, _ = sys.exc_info()
	return HttpResponseServerError(template.render({
		'date_now': now(r"Y-m-d\TH:m:sO"),
		'exception_type': except_type.__name__,
		'exception_value': value,
		'request': request
	}))


def error_404(request, exception, template_name='404.html'):
	template = get_template(template_name)
	ctx = {
		'date_now': now(r"Y-m-d\TH:m:sO"),
		'request': request,
	}
	print(type(exception))
	if isinstance(exception, Http404) and not isinstance(exception, Resolver404):
		ctx['detail'] = exception
	return HttpResponseNotFound(template.render(ctx))


class Home(TemplateView):
	template_name = 'home.html'

	@cached_method(tag='article.article')
	def get_articles(self):
		DEFER = ('original_content', 'filtered_content', 'original_annotation', 'filtered_annotation')
		try:
			top_articles = (Article.objects.all()
				.defer(*DEFER)
				.filter(top=True))
		except IndexError:
			top_articles = Article.objects.all().none()
		articles = (Article.objects.all()
			.select_related('presentation_image')
			.defer(*DEFER))

		articles = list(articles.select_related('author', 'category')[:5])
		top_articles = list(top_articles.select_related('author', 'category')[:1])
		return articles, top_articles

	@cached_method(tag='blog.post')
	def get_posts(self):
		posts = Post.objects.select_related('blog', 'blog__author', 'category', 'series')
		try:
			top_posts = posts.filter(linux=True)[:1]
		except IndexError:
			top_posts = posts.none()
		posts = posts.all()
		return list(posts[:8]), list(top_posts)

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

		new_articles = list(articles[:2])
		new_posts = list(posts[:8])
		new_items = new_articles + new_posts

		ctx.update({
			'top_articles': top_articles,
			'articles': articles,
			'top_posts': top_posts,
			'posts': posts,
			'new_articles': new_articles,
			'new_posts': new_posts,
			'forum_new': forum_new,
			'forum_no_comments': forum_no_comments,
			'forum_most_comments': forum_most_comments,
			'new_items': new_items,
			'article_categories': Category.objects.all(),
			'desktops': self.get_desktops(),
			'tweets': Tweet.objects.order_by('-pk').prefetch_related('author')[:2]
		})
		return ctx
