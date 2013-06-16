# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.response import TemplateResponse
from common_utils.generic import DetailUserProtectedView

from models import Article, Category


class ArticleDetailView(DetailUserProtectedView):
	published_field = 'published'
	author_field = 'author'
	queryset = Article.all_articles.all()


def article_list(request, category = None, page = 1):
	articles = Article.objects.defer('content').select_related('author', 'category')
	category_object = None
	if category is not None:
		category_object = get_object_or_404(Category, slug = category)
		articles = articles.filter(category = category_object)

	context = {
		'articles': articles,
		'category': category_object,
		'pagenum': page,
		'article_categories': Category.objects.all(),
	}
	return TemplateResponse(request, "article/article_list.html", RequestContext(request, context))
