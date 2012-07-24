# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.template import RequestContext
from models import Article

def article_detail_by_slug(request, slug):
	article = get_object_or_404(Article, slug = slug)
	context = {
		'article': article,
	}
	return TemplateResponse(request, "article/article_detail.html", RequestContext(request, context))


def article_list(request):
	articles = Article.articles.all()
	context = {
		'articles': articles,
	}
	return TemplateResponse(request, "article/article_list.html", RequestContext(request, context))
