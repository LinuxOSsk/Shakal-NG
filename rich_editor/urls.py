# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'rich_editor'

urlpatterns = [
	url(r'^preview/$', views.Preview.as_view(), name='preview'),
]
