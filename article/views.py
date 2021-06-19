# -*- coding: utf-8 -*-
from django.db.models import Count, Max

from .models import Article, Category, Series
from common_utils.generic import DetailUserProtectedView, ListView


class ArticleDetailView(DetailUserProtectedView):
	published_field = 'published'
	author_field = 'author'

	def get_queryset(self):
		return Article.all_articles.all()


class ArticleListView(ListView):
	category_model = Category
	paginate_by = 10

	def get_articles_queryset(self):
		return (Article.objects.all()
			.defer('original_content', 'filtered_content')
			.select_related('author', 'category'))

	def get_queryset(self):
		return self.filter_by_category(self.get_articles_queryset())


class ArticleSeriesView(ArticleListView):
	category_model = Series
	category_field = 'series__series'
	paginate_by = 10

	def get_articles_queryset(self):
		return (Article.objects.all()
			.defer('original_content', 'filtered_content')
			.select_related('author', 'category')
			.order_by('series__pk'))


class SeriesListView(ListView):
	paginate_by = 10

	def get_queryset(self):
		return (Series.objects
			.all()
			.annotate(
				last_article=Max('seriesarticle__article__created'),
				count_articles=Count('seriesarticle__article'))
			.order_by('-last_article'))
