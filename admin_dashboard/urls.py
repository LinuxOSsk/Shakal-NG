# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'admin_dashboard'

urlpatterns = [
	url(r'^stats/$', views.Stats.as_view(), name='stats'),
]
