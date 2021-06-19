# -*- coding: utf-8 -*-
from django.urls import path

from . import feeds, views


app_name = 'article'

urlpatterns = [
	path('<page:page>', views.ArticleListView.as_view(), name='list'),
	path('<slug:slug>/', views.ArticleDetailView.as_view(), name='detail'),
	path('kategoria/<slug:category>/<page:page>', views.ArticleListView.as_view(), name='list-category'),
	path('serial/zoznam/<page:page>', views.SeriesListView.as_view(), name='series'),
	path('serial/<slug:category>/<page:page>', views.ArticleSeriesView.as_view(), name='list-series'),
	path('feeds/latest/', feeds.LatestArticleFeed(), name='feed-latest'),
]
