# -*- coding: utf-8 -*-
from django.urls import path

from . import views


app_name = 'wiki'

urlpatterns = [
	path('', views.WikiHomeView.as_view(), name='home'),
	path('<slug:slug>/create/', views.PageCreateView.as_view(), name='create'),
	path('<slug:slug>/edit/', views.PageUpdateView.as_view(), name='edit'),
	path('<slug:slug>/history/<int:history>/', views.WikiDetailView.as_view(), name='page-history'),
	path('<slug:slug>/<page:page>', views.WikiDetailView.as_view(), name='page'),
]
