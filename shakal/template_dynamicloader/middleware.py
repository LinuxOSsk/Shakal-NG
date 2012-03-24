from threading import local

_thread_local = local()

def get_request():
	return getattr(_thread_local, 'request', None)

class RequestMiddleware(object):
	def process_request(self, request):
		setattr(_thread_local, 'request', request)

