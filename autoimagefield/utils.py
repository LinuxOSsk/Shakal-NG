# -*- coding: utf-8 -*-
from django.conf import settings
from easy_thumbnails.files import ThumbnailerFieldFile


def thumbnail(obj, **kwargs):
	thumbnailer = ThumbnailerFieldFile(obj.instance, obj.field, obj.name)
	try:
		return thumbnailer.get_thumbnail(kwargs)
	except Exception:
		if getattr(settings, 'THUMBNAIL_DEBUG', False):
			raise
