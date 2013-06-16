# -*- coding: utf-8 -*-

from common_utils.generic import DetailUserProtectedView, ListView
from models import Article, Category


class ArticleDetailView(DetailUserProtectedView):
	published_field = 'published'
	author_field = 'author'
	queryset = Article.all_articles.all()


class ArticleListView(ListView):
	queryset = Article.objects.defer('content').select_related('author', 'category')
	category = Category
