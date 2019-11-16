# -*- coding: utf-8 -*-
from django.urls import path

from . import views


app_name = 'image_renderer'

urlpatterns = [
	path('<slug:image_type>/<int:content_type>/<path:object_id>.png', views.RenderImageView.as_view(), name='render'),
]
