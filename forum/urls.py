# -*- coding: utf-8 -*-
from django.urls import path, reverse_lazy
from django.views.generic.base import RedirectView

from . import feeds, views


app_name = 'forum'

urlpatterns = [
	path('', RedirectView.as_view(url=reverse_lazy('forum:overview', kwargs={'page': 1}), permanent=False)),
	path('prehlad/<page:page>', views.TopicListView.as_view(), name='overview'),
	path('pridat/', views.TopicCreateView.as_view(), name='create'),
	path('<int:pk>/', views.TopicDetailView.as_view(), name='topic-detail'),
	path('<slug:category>/<page:page>', views.TopicListView.as_view(), name='section'),
	path('feeds/latest/', feeds.TopicFeed(), name='feed-latest'),
]
