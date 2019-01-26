# -*- coding: utf-8 -*-

from django.urls import path

from . import views


app_name = 'rating'

urlpatterns = [
	path('flag/<int:content_type>/<int:object_id>/', views.FlagView.as_view(), name='flag'),
	path('ratings/<int:pk>/', views.RatingsView.as_view(), name='ratings'),
]
