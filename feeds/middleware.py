# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .register import FeedsRegister


class FeedsMiddleware(object):
	def process_request(self, request):
		setattr(request, '_feeds', FeedsRegister())
