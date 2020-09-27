# -*- coding: utf-8 -*-
from django.urls import path

from . import views


app_name = 'fulltext'


urlpatterns = [
	path('<page:page>', views.SearchView.as_view(), name='search'),
]
