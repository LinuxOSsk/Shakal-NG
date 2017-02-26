# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.conf import settings
from django_jinja import library

from autoimagefield.utils import thumbnail as create_thumbnail


logger = logging.getLogger('shakal')


@library.global_function
def thumbnail(source_url, **kwargs):
	try:
		return create_thumbnail(source_url, **kwargs).url
	except Exception: #pylint: disable=broad-except
		if getattr(settings, 'THUMBNAIL_DEBUG', False):
			raise
		else:
			logger.exception("Thumbnail not created")
