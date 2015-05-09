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
