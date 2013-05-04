# -*- coding: utf-8 -*-

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shakal.settings")

from django_extensions.management.utils import RedirectHandler
import logging
logging.getLogger(__name__)

werklogger = logging.getLogger('werkzeug')
werklogger.setLevel(logging.INFO)
werklogger.addHandler(RedirectHandler(__name__))
werklogger.propagate = False

from django.template import TemplateSyntaxError
from django.views.debug import technical_500_response
def null_technical_500_response(request, exc_type, exc_value, tb):
	if request.META['REMOTE_ADDR'] == '127.0.0.1' and exc_type != TemplateSyntaxError:
		raise exc_type, exc_value, tb
	else:
		return technical_500_response(request, exc_type, exc_value, tb)


from django.views import debug
debug.technical_500_response = null_technical_500_response


from werkzeug import DebuggedApplication
from django.core.wsgi import get_wsgi_application
application = DebuggedApplication(get_wsgi_application(), True)
