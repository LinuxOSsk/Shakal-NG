# -*- coding: utf-8 -*-
import os

import socket
from django.http import HttpResponse


def status(request): #pylint: disable=unused-argument
	status_data = "{}"
	address = os.path.abspath("maintenance.flag")
	if (os.path.exists(address)):
		status_data = "{text: '...'}"
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	try:
		sock.connect(address)
		status_data = sock.recv(65536)
	except socket.error:
		pass
	return HttpResponse(status_data, content_type='application/json')
