# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path

from . import views


app_name = 'rich_editor'

urlpatterns = [
	path('preview/', views.Preview.as_view(), name='preview'),
]
