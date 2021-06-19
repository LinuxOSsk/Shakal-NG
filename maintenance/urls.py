# -*- coding: utf-8 -*-
from django.urls import path

from . import views


app_name = 'maintenance'

urlpatterns = [
	path('stav/', views.status, name='status'),
]
