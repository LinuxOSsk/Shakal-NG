# -*- coding: utf-8 -*-
import re

from django.conf import settings

from common_utils import get_current_request


def get_available_size(content_type, uploaded_size):
	max_size = getattr(settings, 'ATTACHMENT_MAX_SIZE', -1)
	db_table = "{0}_{1}".format(content_type.app_label, content_type.model)
	size_for_content = getattr(settings, 'ATTACHMENT_SIZE_FOR_CONTENT', {}).get(db_table, None)
	# Obsah bez limitu
	if size_for_content is None:
		return max_size
	# Bez limitu
	if max_size < 0 and size_for_content < 0:
		return -1
	if size_for_content < 0:
		return -1
	return max(size_for_content - uploaded_size, 0)


def replace_file_urls(val, moves):
	host = ''
	req = get_current_request()
	if req is not None:
		host = req.scheme + '://' + req.get_host()
	for src, dst in moves:
		src_dir = '/'.join(src.split('/')[:-1])
		dst_dir = '/'.join(dst.split('/')[:-1])
		val = re.sub('(' + re.escape(host) + ')?' + re.escape(settings.MEDIA_URL + src_dir), settings.MEDIA_URL + dst_dir, val)
	return val
