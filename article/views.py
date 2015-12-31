# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import Article, Category
from common_utils.generic import DetailUserProtectedView, ListView


class ArticleDetailView(DetailUserProtectedView):
	published_field = 'published'
	author_field = 'author'

	def get_queryset(self):
		return Article.all_articles.all()


class ArticleListView(ListView):
	category_model = Category
	paginate_by = 10

	def get_queryset(self):
		return (Article.objects.all()
			.defer('original_content', 'filtered_content')
			.select_related('author', 'category'))
