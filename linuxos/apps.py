# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete


class LinuxosConfig(AppConfig):
	name = 'linuxos'
	verbose_name = 'LinuxOS'

	def ready(self):
		from .utils import clear_cache

		post_save.connect(clear_cache)
		post_delete.connect(clear_cache)
