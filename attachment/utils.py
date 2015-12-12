# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.conf import settings


def get_available_size(content_type, uploaded_size):
	max_size = getattr(settings, 'ATTACHMENT_MAX_SIZE', -1)
	db_table = "{0}_{1}".format(content_type.app_label, content_type.model)
	size_for_content = getattr(settings, 'ATTACHMENT_SIZE_FOR_CONTENT', {}).get(db_table, None)
	# Bez limitu
	if max_size < 0 and size_for_content < 0:
		return -1
	# Obsah bez limitu
	if size_for_content is None:
		return max_size
	if size_for_content < 0:
		return -1
	return max(size_for_content - uploaded_size, 0)


def replace_file_urls(val, moves):
	for src, dst in moves:
		val = re.sub(re.escape(settings.MEDIA_URL + src), settings.MEDIA_URL + dst, val)
	return val
