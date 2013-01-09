# -*- coding: utf-8 -*-

class FeedsMiddleware(object):
	def process_request(self, request):
		setattr(request, '_feeds', [])
