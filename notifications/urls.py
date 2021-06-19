# -*- coding: utf-8 -*-
from django.urls import path

from . import views


app_name = 'notifications'

urlpatterns = [
	path('', views.List.as_view(), name='list'),
	path('r/<int:pk>/', views.Read.as_view(), name='read'),
]
