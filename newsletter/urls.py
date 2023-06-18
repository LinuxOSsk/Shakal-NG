# -*- coding: utf-8 -*-
from django.conf import settings
from django.urls import path, register_converter

from . import views


urlpatterns = [
	path('subscribe/', views.NewsletterSubscribeView.as_view(), name='subscribe'),
]


if settings.DEBUG:
	class FormatConverter:
		regex = 'html|txt'

		def to_python(self, value):
			return value

		def to_url(self, value):
			return value

	register_converter(FormatConverter, 'newsletter_format')

	urlpatterns += [
		path('week-<date:date>.<newsletter_format:format>', views.WeeklyNewsletterPreview.as_view(), name='weekly_newsletter'),
	]
