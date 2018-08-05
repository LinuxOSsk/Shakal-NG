# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path

from . import feeds, views


app_name = 'blog'

urlpatterns = [
	path('admin/update/', views.BlogUpdateView.as_view(), name='blog-update'),
	path('<page:page>', views.PostListView.as_view(), name='post-list'),
	path('admin/create-post/', views.PostCreateView.as_view(), name='post-create'),
	path('admin/my/', views.MyBlogView.as_view(), name='my'),
	path('<slug:category>/list/<page:page>', views.PostListView.as_view(), name='post-list-category'),
	path('<slug:category>/detail/<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),
	path('<slug:category>/update/<slug:slug>/', views.PostUpdateView.as_view(), name='post-update'),
	path('<slug:category>/update/<slug:slug>/attachments/', views.PostAttachmentsUpdateView.as_view(), name='post-attachments-update'),
	path('feeds/latest/', feeds.PostFeed(), name='post-feed-latest'),
	path('feeds/linux/', feeds.PostFeed(linux=True), name='post-feed-linux'),
	path('<slug:blog_slug>/feed/', feeds.PostFeed(), name='post-feed-blog'),
]
