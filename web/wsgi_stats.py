# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from guppy import hpy

from .wsgi import application


class StatsMiddleware(object):
	def __init__(self, app):
		super(StatsMiddleware, self).__init__()
		self.app = app
		self.hp = hpy()
		self.heap_start = None
		self.heap_end = None

	def empty_response(self, start_response):
		status = str('200 OK')
		response_headers = [(str('Content-type'), str('text/plain'))]
		start_response(status, response_headers)
		return [str('')]

	def __call__(self, environ, start_response):
		if 'debugmem' in environ.get('QUERY_STRING', ''):
			heap_data = [str(self.hp.heap())]
			for item in self.empty_response(start_response):
				yield item
			for item in heap_data:
				yield item
		else:
			#start = timer()
			#from timeit import default_timer as timer
			for item in self.app(environ, start_response):
				yield item
			#end = timer()
			#time = end - start


application = StatsMiddleware(application)
