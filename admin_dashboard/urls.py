# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path

from . import views


app_name = 'admin_dashboard'

urlpatterns = [
	path('stats/', views.Stats.as_view(), name='stats'),
]
