# -*- coding: utf-8 -*-
import os

from template_dynamicloader.utils import get_template_settings

from web.middlewares.threadlocal import get_current_request


class DynamicLoaderMixin(object):
	def get_dynamic_template(self):
		request = get_current_request()
		return get_template_settings(request).template

	def get_visitors_template_dir(self):
		return os.path.join('template_overrides', self.get_dynamic_template())

	def get_visitors_template(self, template_name):
		return os.path.join(self.get_visitors_template_dir(), template_name)
