# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django_jinja import library
from easy_thumbnails.files import ThumbnailFile

from autoimagefield.utils import thumbnail as create_thumbnail


logger = logging.getLogger('shakal')


def get_url(self):
	return self.url or ''
ThumbnailFile.__str__ = get_url


@library.global_function
def thumbnail(source_url, **kwargs):
	try:
		thumbnail = create_thumbnail(source_url, **kwargs)
		return thumbnail
	except Exception: #pylint: disable=broad-except
		if getattr(settings, 'THUMBNAIL_DEBUG', False):
			raise
		else:
			logger.exception("Thumbnail not created")
