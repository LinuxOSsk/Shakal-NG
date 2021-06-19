# -*- coding: utf-8 -*-
from django.urls import path

from . import views


app_name = 'admin_dashboard'

urlpatterns = [
	path('stats/', views.Stats.as_view(), name='stats'),
]
