# -*- coding: utf-8 -*-
import base64
import hashlib


def default(source_filename, prepared_options, thumbnail_extension, **kwargs):
	fmt = kwargs.get('thumbnail_options', {}).get('format')
	if fmt:
		thumbnail_extension = f'{thumbnail_extension}.{fmt}'
		prepared_options = [opt for opt in prepared_options if opt != f'format-{fmt}']
	digest = hashlib.sha1(':'.join(prepared_options).encode('utf-8')).digest()
	safe_hash = base64.urlsafe_b64encode(digest[:(len(digest)//3)*3]).decode('utf-8')
	return '.'.join([source_filename, '_'.join(prepared_options[:1] + [safe_hash]), thumbnail_extension])
