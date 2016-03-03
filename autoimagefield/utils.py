# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from easy_thumbnails.files import get_thumbnailer


def thumbnail(source_url, **kwargs):
	thumbnailer = get_thumbnailer(source_url)
	return thumbnailer.get_thumbnail(kwargs)
