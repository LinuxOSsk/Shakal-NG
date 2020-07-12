# -*- coding: utf-8 -*-
from django.apps import AppConfig as BaseAppConfig
from django.utils.module_loading import autodiscover_modules


class AppConfig(BaseAppConfig):
	name = 'fulltext'
	verbose_name = "Fulltext"

	def ready(self):
		autodiscover_modules('fulltext_search')
