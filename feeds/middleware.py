# -*- coding: utf-8 -*-
from .register import FeedsRegister


class FeedsMiddleware(object):
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		setattr(request, '_feeds', FeedsRegister())
		return self.get_response(request)
