# -*- coding: utf-8 -*-
from django.urls import path

from . import feeds, views


app_name = 'tweets'

urlpatterns = [
	path('detail/<slug:slug>/', views.TweetDetailView.as_view(), name='detail'),
	path('pridat/', views.TweetCreateView.as_view(), name='create'),
	path('upravit/<slug:slug>/', views.TweetUpdateView.as_view(), name='update'),
	path('<page:page>', views.TweetListView.as_view(), name='list'),
	path('feeds/latest/', feeds.TweetFeed(), name='feed-latest'),
]
