# -*- coding: utf-8 -*-
from django.urls import path

from . import views


app_name = 'blackhole'

urlpatterns = [
	path('clanky/<page:page>', views.StoryList.as_view(), name='story_list'),
	path('clanky/kategoria/<int:category>/<page:page>', views.StoryList.as_view(), name='story_list_term'),
	path('clanok/<int:pk>/', views.StoryDetail.as_view(), name='story_detail'),
]
