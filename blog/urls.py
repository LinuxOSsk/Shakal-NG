# -*- coding: utf-8 -*-
from django.urls import path

from . import feeds, views


app_name = 'blog'

urlpatterns = [
	path('admin/update/', views.BlogUpdateView.as_view(), name='blog-update'),
	path('<page:page>', views.PostListView.as_view(), name='post-list'),
	path('admin/create-post/', views.PostCreateView.as_view(), name='post-create'),
	path('admin/my/', views.MyBlogView.as_view(), name='my'),
	path('<slug:blog>/list/<page:page>', views.PostListView.as_view(), name='post-list-blog'),
	path('<slug:blog>/categories/manage/', views.PostCategoryManagementList.as_view(), name='post-category-management-list'),
	path('<slug:blog>/categories/create/', views.PostCategoryCreateView.as_view(), name='post-category-management-create'),
	path('<slug:blog>/categories/update/<int:pk>/', views.PostCategoryUpdateView.as_view(), name='post-category-management-update'),
	path('<slug:blog>/categories/delete/<int:pk>/', views.PostCategoryDeleteView.as_view(), name='post-category-management-delete'),
	path('<slug:blog>/series/manage/', views.PostSeriesManagementList.as_view(), name='post-series-management-list'),
	path('<slug:blog>/series/create/', views.PostSeriesCreateView.as_view(), name='post-series-management-create'),
	path('<slug:blog>/series/update/<int:pk>/', views.PostSeriesUpdateView.as_view(), name='post-series-management-update'),
	path('<slug:blog>/series/delete/<int:pk>/', views.PostSeriesDeleteView.as_view(), name='post-series-management-delete'),
	path('<slug:blog>/detail/<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),
	path('<slug:blog>/update/<slug:slug>/', views.PostUpdateView.as_view(), name='post-update'),
	path('<slug:blog>/update/<slug:slug>/attachments/', views.PostAttachmentsUpdateView.as_view(), name='post-attachments-update'),
	path('<slug:blog>/list/<slug:category>/<page:page>', views.PostListView.as_view(), name='post-list-blog-category'),
	path('<slug:blog>/series/<slug:series>/<page:page>', views.PostListView.as_view(), name='post-list-blog-series'),
	path('feeds/latest/', feeds.PostFeed(), name='post-feed-latest'),
	path('feeds/linux/', feeds.PostFeed(linux=True), name='post-feed-linux'),
	path('<slug:blog_slug>/feed/', feeds.PostFeed(), name='post-feed-blog'),
]
