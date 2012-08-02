# -*- coding: utf-8 -*-

from django.db.models import Q
from django.template import RequestContext
from django.template.response import TemplateResponse
from article.models import article_model, Category as ArticleCategory
from forum.models import Topic as ForumTopic

def home(request):
	try:
		top_article = article_model().articles.filter(top = True).all()[0]
		articles = article_model().articles.filter(~Q(pk = top_article.pk)).all()
	except IndexError:
		top_article = None
		articles = article_model().articles.all()

	context = {
		'top_article': top_article,
		'articles': articles[:5],
		'article_categories': ArticleCategory.objects.all(),
		'forum_new': ForumTopic.objects.order_by('-pk').all()[:20],
		'forum_no_comments': ForumTopic.objects.order_by('-pk').all()[:5],
		'forum_most_comments': ForumTopic.objects.order_by('-pk').all()[:5],
	}
	return TemplateResponse(request, "home.html", RequestContext(request, context))
