# -*- coding: utf-8 -*-
import sys

from django.http import HttpResponseServerError
from django.template.loader import get_template
from django.views.generic import TemplateView
from common_utils.cache import cached_method

from article.models import Article, Category
from blog.models import Post
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
	return HttpResponseServerError(template.render({
		'date_now': now(r"Y-m-d\TH:m:sO"),
		'request': request,
	}))


class Home(TemplateView):
	template_name = 'home.html'

	@cached_method(tag='article.Article')
	def get_articles(self):
		try:
			top_articles = Article.objects.all().filter(top=True)
			articles = Article.objects.all().exclude(pk=top_articles[0].pk)
		except IndexError:
			top_articles = Article.objects.all().none()
			articles = Article.objects.all()

		articles = list(articles.select_related('author', 'category').defer('content')[:5])
		top_articles = list(top_articles.select_related('author', 'category').defer('content')[:1])
		return articles, top_articles

	def get_context_data(self, **kwargs):
		ctx = super(Home, self).get_context_data(**kwargs)
		articles, top_articles = self.get_articles()
		ctx.update({
			'top_articles': top_articles,
			'articles': articles,
		})
		return ctx

		#try:
		#	top_posts = Post.objects.all().filter(linux=True)
		#	posts = Post.objects.all().exclude(pk=top_posts[0].pk)
		#except IndexError:
		#	top_posts = Post.objects.all().none()
		#	posts = Post.objects.all()

		#ctx.update({
		#	'top_articles': top_articles,
		#	'articles': articles,
		#	'top_posts': top_posts[:1],
		#	'posts': posts[:4],
		#	'forum_new': ForumTopic.topics.newest_comments()[:20],
		#	'forum_no_comments': ForumTopic.topics.no_comments()[:5],
		#	'forum_most_comments': ForumTopic.topics.most_commented()[:5],
		#	'article_categories': Category.objects.all(),
		#})
		#return ctx
