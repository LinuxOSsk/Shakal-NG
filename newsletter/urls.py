# -*- coding: utf-8 -*-
from django.urls import path

from . import views


urlpatterns = [
	path('subscribe/', views.NewsletterSubscribeView.as_view(), name='subscribe'),
]
