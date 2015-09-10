# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import Article, Category
from common_utils.generic import DetailUserProtectedView, ListView


class ArticleDetailView(DetailUserProtectedView):
	published_field = 'published'
	author_field = 'author'
	queryset = Article.all_articles.all()


class ArticleListView(ListView):
	queryset = Article.objects.all().defer('content').select_related('author', 'category')
	category_model = Category
	paginate_by = 10
