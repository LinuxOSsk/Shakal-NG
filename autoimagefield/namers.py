# -*- coding: utf-8 -*-
from easy_thumbnails import namers


def default(thumbnailer, prepared_options, source_filename, thumbnail_extension, **kwargs):
	fmt = kwargs.get('thumbnail_options', {}).get('format')
	if fmt:
		thumbnail_extension = fmt
	return namers.default(thumbnailer, prepared_options, source_filename, thumbnail_extension, **kwargs)
