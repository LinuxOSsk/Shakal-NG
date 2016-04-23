# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import namedtuple

from django.core.management.base import BaseCommand
from django.db import connections
from django.utils.functional import cached_property
#from common_utils.asciitable import NamedtupleTablePrinter


FilterFormat = namedtuple('FilterFormat', ['format', 'name'])


FORMATS_TRANSLATION = {
	'Filtered HTML': 'html',
	'PHP code': 'html',
	'Full HTML': 'raw',
	'No HTML': 'text',
}


class Command(BaseCommand):
	@cached_property
	def db_connection(self):
		return connections['blackhole']

	def db_cursor(self):
		return self.db_connection.cursor()

	@cached_property
	def filter_formats(self):
		cursor = self.db_cursor()
		cursor.execute('SELECT format, name FROM filter_formats')
		formats = tuple(FilterFormat(*row) for row in cursor.fetchall())
		return {f.format: FORMATS_TRANSLATION[f.name] for f in formats}

	def handle(self, *args, **options):
		print(self.filter_formats)
