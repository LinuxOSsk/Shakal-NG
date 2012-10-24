# -*- coding: utf-8 -*-

from django.http import HttpResponse
import os
import socket

def status(request):
	status = "{}"
	address = os.path.abspath("maintenance.flag")
	if (os.path.exists(address)):
		status = "{text: '...'}"
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	try:
		sock.connect(address)
		status = sock.recv(65536)
	except socket.error:
		pass
	return HttpResponse(status, mimetype = 'application/json')
