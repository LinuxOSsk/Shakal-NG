# -*- coding: utf-8 -*-
from django.urls import path

from . import feeds, views


app_name = 'desktops'

urlpatterns = [
	path('sprava/vytvorit/', views.DesktopCreate.as_view(), name='create'),
	path('zoznam/<page:page>', views.DesktopList.as_view(), name='list'),
	path('zoznam/autor/<int:category>/<page:page>', views.DesktopList.as_view(), name='list-author'),
	path('detail/<int:pk>/', views.DesktopDetail.as_view(), name='detail'),
	path('upravit/<int:pk>/', views.DesktopUpdate.as_view(), name='update'),
	path('feeds/latest/', feeds.DesktopFeed(), name='feed-latest'),
]
