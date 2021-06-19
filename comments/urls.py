# -*- coding: utf-8 -*-
from django.urls import path

from . import feeds, views


app_name = 'comments'

urlpatterns = [
	path('odpovedat/<int:parent>/', views.Reply.as_view(), name='reply'),
	path('zamknut/<int:pk>/', views.Admin.as_view(), name='admin'),
	path('sledovat/<int:pk>/', views.Watch.as_view(), name='watch'),
	path('zabudnut/<int:pk>/', views.Forget.as_view(), name='forget'),
	path('pocet/<int:ctype>/<int:pk>/', views.CommentCountImage.as_view(), name='count-image'),
	path('<int:pk>/', views.Comments.as_view(), name='comments'),
	path('zobrazit/<int:pk>/', views.CommentDetailSingle.as_view(), name='comment-single'),
	path('id/<int:pk>/', views.CommentDetail.as_view(), name='comment'),
	path('feeds/latest/', feeds.CommentFeed(), name='feed-latest'),
]
