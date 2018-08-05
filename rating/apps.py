# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
	name = 'rating'
	verbose_name = "Hlasovanie"
