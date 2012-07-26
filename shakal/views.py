# -*- coding: utf-8 -*-

from django.db.models import Q
from django.template import RequestContext
from django.template.response import TemplateResponse
from article.models import Article

def home(request):
	try:
		top_article = Article.articles.filter(top = True).all()[0]
		articles = Article.articles.filter(~Q(pk = top_article.pk)).all()
	except IndexError:
		top_article = None
		articles = Article.articles.all()

	context = {
		'top_article': top_article,
		'articles': articles[:5]
	}
	return TemplateResponse(request, "home.html", RequestContext(request, context))
