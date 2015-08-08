# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .wsgi import application
from timeit import default_timer as timer
from guppy import hpy


class StatsMiddleware(object):
	def __init__(self, app):
		super(StatsMiddleware, self).__init__()
		self.app = app
		self.hp = hpy()

	def __call__(self, environ, start_response):
		start = timer()
		heap_before = self.hp.heap()
		for item in self.app(environ, start_response):
			yield item
		heap_after = self.hp.heap()
		end = timer()
		time = end - start
		heap_diff = heap_after - heap_before
		print(time)
		print(heap_diff)
		if 'debugmem' in environ.get('QUERY_STRING', ''):
			import pdb; pdb.set_trace()


application = StatsMiddleware(application)
