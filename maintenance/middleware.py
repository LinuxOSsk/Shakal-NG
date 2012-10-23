# -*- coding: utf-8 -*-

import os
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import RequestContext

class MaintenanceMiddleware(object):
	def process_request(self, request):
		if not os.path.exists("maintenance.flag"):
			return None
		response = render_to_string("503.html", {}, context_instance = RequestContext(request))
		return HttpResponse(response, status = 503)
