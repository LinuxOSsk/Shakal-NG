# -*- coding: utf-8 -*-
from django.apps import AppConfig as BaseAppConfig
from django.db.models.signals import post_save, post_delete
from django.utils.module_loading import autodiscover_modules


class AppConfig(BaseAppConfig):
	name = 'fulltext'
	verbose_name = "Fulltext"

	def ready(self):
		from .utils import schedule_update_fulltext, schedule_delete_fulltext
		autodiscover_modules('fulltext_search')
		post_save.connect(schedule_update_fulltext)
		post_delete.connect(schedule_delete_fulltext)
