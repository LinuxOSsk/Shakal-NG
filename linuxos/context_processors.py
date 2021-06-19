# -*- coding: utf-8 -*-
from django.conf import settings as django_settings


def settings(request):
	return {
		'ANONYMOUS_COMMENTS': django_settings.ANONYMOUS_COMMENTS,
	}
