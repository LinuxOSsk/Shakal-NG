# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path

from . import views


app_name = 'polls'

urlpatterns = [
	path('detail/<slug:slug>/', views.PollDetail.as_view(), name='detail-by-slug'),
	path('<page:page>', views.PollList.as_view(), name='list'),
	path('post/<int:pk>/', views.PollPost.as_view(), name='post'),
	path('vytvorit/', views.PollCreate.as_view(), name='create'),
]
