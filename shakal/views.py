# -*- coding: utf-8 -*-

from django.http import HttpResponseServerError, HttpResponse
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.template.response import TemplateResponse
from article.models import Article, Category
from forum.models import Topic as ForumTopic
import sys


def error_500(request):
	template = get_template('500.html')
	type, value, tb = sys.exc_info()
	return HttpResponseServerError(template.render(Context({
		'exception_type': type.__name__,
		'exception_value': value,
		'request': request
	})))


def home(request):
	try:
		top_articles = Article.objects.filter(top = True)
		articles = Article.objects.exclude(pk = top_articles[0].pk)
	except IndexError:
		top_articles = Article.objects.none()
		articles = Article.objects.all()

	articles = articles.select_related('author', 'category').defer('content')
	top_articles = top_articles.select_related('author', 'category').defer('content')

	context = {
		'top_articles': top_articles[:1],
		'articles': articles[:5],
		'forum_new': ForumTopic.topics.newest_comments()[:20],
		'forum_no_comments': ForumTopic.topics.no_comments()[:5],
		'forum_most_comments': ForumTopic.topics.most_commented()[:5],
		'article_categories': Category.objects.all(),
	}
	return TemplateResponse(request, "home.html", RequestContext(request, context))
