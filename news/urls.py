# -*- coding: utf-8 -*-
from django.urls import path

from . import feeds, views


app_name = 'news'

urlpatterns = [
	path('detail/<slug:slug>/', views.NewsDetailView.as_view(), name='detail'),
	path('detail/<slug:slug>/upravit/', views.NewsUpdateView.as_view(), name='update'),
	path('detail/<slug:slug>/poznamka/', views.NoteCreate.as_view(), name='note-create'),
	path('pridat/', views.NewsCreateView.as_view(), name='create'),
	path('<page:page>', views.NewsListView.as_view(), name='list'),
	path('kategoria/<slug:category>/<page:page>', views.NewsListView.as_view(), name='list-category'),
	path('feeds/latest/', feeds.NewsFeed(), name='feed-latest'),
	path('udalosti/<page:page>', views.EventListView.as_view(), name='event-list'),
	path('udalosti/kategoria/<slug:category>/<page:page>', views.EventListView.as_view(), name='event-list-category'),
]
