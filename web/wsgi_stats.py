# -*- coding: utf-8 -*-
from guppy import hpy

from .wsgi import application


class StatsMiddleware(object):
	def __init__(self, app):
		super(StatsMiddleware, self).__init__()
		self.app = app
		self.hp = hpy()

	def start_ok_response(self, start_response):
		status = '200 OK'
		response_headers = [('Content-type', 'text/plain')]
		start_response(status, response_headers)

	def __call__(self, environ, start_response):
		if 'debugmem_dump' in environ.get('QUERY_STRING', ''):
			heap = self.hp.heap()
			heap.dump('profile.hpy')
			heap_response = [
				#'\nHeap\n',
				#str(heap),
				#'\nrcs\n',
				#str(heap.byrcs),
				#'\nrcs[0]\n',
				#str(heap.byrcs[0].byid),
				#'\nrp\n',
				#str(heap.get_rp()),
				#'\nModules\n',
				#str(heap.bymodule),
			]
			self.start_ok_response(start_response)
			for item in heap_response:
				yield item
		elif 'debugmem_live' in environ.get('QUERY_STRING', ''):
			heap = self.hp.heap()
			self.start_ok_response(start_response)
			import pdb
			pdb.set_trace()
		elif 'debugmem_relheap' in environ.get('QUERY_STRING', ''):
			self.hp.setrelheap()
			self.start_ok_response(start_response)
		else:
			#start = timer()
			#from timeit import default_timer as timer
			for item in self.app(environ, start_response):
				yield item
			#end = timer()
			#time = end - start


application = StatsMiddleware(application)
