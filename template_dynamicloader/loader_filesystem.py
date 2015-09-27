# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from template_dynamicloader.utils import get_template_settings

from common_utils.middlewares.ThreadLocal import get_current_request


class DynamicLoaderMixin(object):
	def get_visitors_template_dir(self):
		request = get_current_request()
		template_skin = get_template_settings(request)[0]
		return os.path.join('template_overrides', template_skin.split(',')[0])

	def get_visitors_template(self, template_name):
		return os.path.join(self.get_visitors_template_dir(), template_name)
