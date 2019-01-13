# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.apps import AppConfig as CoreAppConfig
from django.db.models.signals import pre_save

from common_utils import get_meta, get_current_request, get_client_ip


SET_IP_MODELS = {
	('comments', 'comment'),
	('forum', 'topic'),
}


class AppConfig(CoreAppConfig):
	name = 'common_utils'
	verbose_name = 'Utility'

	def ready(self):
		self.patch_migrations()
		pre_save.connect(self.set_ip_for_object)

	def patch_migrations(self):
		from django.db.migrations.writer import MigrationWriter
		rx = re.compile('^(    )+', flags=re.MULTILINE)
		replace = lambda match: '\t'*(len(match.group())//4)
		old_as_string = MigrationWriter.as_string
		MigrationWriter.as_string = lambda self: rx.sub(replace, old_as_string(self))

	def set_ip_for_object(self, instance, **kwargs):
		opts = get_meta(instance)
		model = (opts.app_label, opts.model_name)
		if model in SET_IP_MODELS:
			request = get_current_request()
			if request:
				instance.ip_address = get_client_ip(request)
