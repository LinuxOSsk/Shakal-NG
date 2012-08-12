# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.template import RequestContext
from models import Article, Category

def article_detail_by_slug(request, slug):
	article = get_object_or_404(Article.objects.select_related('author', 'category'), slug = slug)
	article.hit()
	context = {
		'article': article,
	}
	return TemplateResponse(request, "article/article_detail.html", RequestContext(request, context))


def article_list(request, category = None, page = 1):
	articles = Article.articles
	category_object = None
	if category is not None:
		category_object = get_object_or_404(Category, slug = category)
		#articles = articles.filter(category = category_object)

	context = {
		'articles': articles.all(),
		'category': category_object,
		'pagenum': page,
	}
	return TemplateResponse(request, "article/article_list.html", RequestContext(request, context))
