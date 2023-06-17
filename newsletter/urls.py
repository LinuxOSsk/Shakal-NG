# -*- coding: utf-8 -*-
from django.urls import path

from . import views


urlpatterns = [
	path('signup/', views.NewsletterSignupView.as_view(), name='signup'),
]
