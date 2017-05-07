# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from template_dynamicloader.utils import get_template_settings

from web.middlewares.threadlocal import get_current_request


class DynamicLoaderMixin(object):
	def get_dynamic_template(self):
		request = get_current_request()
		template_skin = get_template_settings(request)[0]
		return template_skin.split(',')[0]

	def get_visitors_template_dir(self):
		return os.path.join('template_overrides', self.get_dynamic_template())

	def get_visitors_template(self, template_name):
		return os.path.join(self.get_visitors_template_dir(), template_name)
