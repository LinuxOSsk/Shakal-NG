# -*- coding: utf-8 -*-
import os

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.functional import cached_property


class MaintenanceMiddleware(object):
	def __init__(self):
		self.ignore_path = reverse_lazy('maintenance:status')

	@cached_property
	def maintenance(self):
		return os.path.exists("maintenance.flag")

	def process_request(self, request):
		if not self.maintenance:
			return None
		if request.path == self.ignore_path:
			return None
		response = render_to_string("503.html", {}, request=request)
		return HttpResponse(response, status=503)
