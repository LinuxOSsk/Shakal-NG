# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
	name = 'tweets'
	verbose_name = "Tweety"
