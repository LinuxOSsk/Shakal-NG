from django.conf import settings
from django.core.urlresolvers import get_resolver
from django.http import Http404
from django.views.debug import technical_404_response


class PaginatorMiddleware(object):
	def process_response(self, request, response):
		if getattr(request, 'paginator_page_not_found', False):
			if settings.DEBUG:
				error = Http404('The requested page number is out of range.')
				return technical_404_response(request, error)
			else:
				callback, params = get_resolver(None).resolve404()
				return callback(request, **params)
		return response
