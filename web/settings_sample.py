# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import,unused-wildcard-import
from __future__ import unicode_literals

from .settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
	'django_extensions',
	#'debug_toolbar',
)

#HAYSTACK_CONNECTIONS = {
#	'default': {
#		'ENGINE': 'xapian_backend.XapianEngine',
#		'PATH': os.path.join(ROOT, 'xapian_index'),
#		'INCLUDE_SPELLING': False
#	},
#}
#HAYSTACK_XAPIAN_LANGUAGE = 'sk'
