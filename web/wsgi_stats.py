# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .wsgi import application
from timeit import default_timer as timer


class StatsMiddleware(object):
	def __init__(self, app):
		super(StatsMiddleware, self).__init__()
		self.app = app

	def __call__(self, environ, start_response):
		start = timer()
		for item in self.app(environ, start_response):
			yield item
		end = timer()
		time = end - start
		print(time)


application = StatsMiddleware(application)
