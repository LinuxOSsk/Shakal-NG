# -*- coding: utf-8 -*-

from django.http import HttpResponseServerError
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.template.response import TemplateResponse
from article.models import Article
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
		top_articles = [Article.objects.select_related('author', 'category').filter(top = True).order_by('-pk')[0:1][0]]
		articles = Article.objects.select_related('author', 'category').exclude(pk = top_articles[0].pk).order_by('-pk')
	except IndexError:
		top_articles = []
		articles = Article.objects.select_related('author', 'category').order_by('-pk')

	context = {
		'top_articles': top_articles,
		'articles': articles[:5],
		'forum_new': ForumTopic.topics.newest_comments()[:20],
		'forum_no_comments': ForumTopic.topics.no_comments()[:5],
		'forum_most_comments': ForumTopic.topics.most_commented()[:5],
	}
	return TemplateResponse(request, "home.html", RequestContext(request, context))
