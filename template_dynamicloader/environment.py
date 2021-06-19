# -*- coding: utf-8 -*-
import jinja2.exceptions

from .loader_filesystem import DynamicLoaderMixin


class Environment(DynamicLoaderMixin, jinja2.Environment):
	def get_template(self, name, *args, **kwargs):
		try:
			return super(Environment, self).get_template(self.get_visitors_template(name), *args, **kwargs)
		except jinja2.exceptions.TemplateNotFound:
			return super(Environment, self).get_template(name, *args, **kwargs)
