# -*- coding: utf-8 -*-
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views


app_name = 'polls'

urlpatterns = [
	path('detail/<slug:slug>/', views.PollDetail.as_view(), name='detail-by-slug'),
	path('<page:page>', views.PollList.as_view(), name='list'),
	path('post/<int:pk>/', csrf_exempt(views.PollPost.as_view()), name='post'),
	path('vytvorit/', views.PollCreate.as_view(), name='create'),
]
