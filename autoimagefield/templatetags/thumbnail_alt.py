# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_jinja import library

from autoimagefield.utils import thumbnail as create_thumbnail


@library.global_function
def thumbnail(source_url, **kwargs):
	return create_thumbnail(source_url, **kwargs).url
