# -*- coding: utf-8 -*-
from django.conf import settings
from django.urls import path, register_converter
from django.views.decorators.csrf import csrf_exempt

from . import views


app_name = 'newsletter'

urlpatterns = [
	path('subscribe/', views.NewsletterSubscribeView.as_view(), name='subscribe'),
	path('unsubscribe/<str:token>/', csrf_exempt(views.NewsletterUnsubscribeView.as_view()), name='unsubscribe'),
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
