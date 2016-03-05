# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from easy_thumbnails.files import ThumbnailerFieldFile


def thumbnail(obj, **kwargs):
	thumbnailer = ThumbnailerFieldFile(obj.instance, obj.field, obj.name)
	return thumbnailer.get_thumbnail(kwargs)
