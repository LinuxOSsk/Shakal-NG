# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import namedtuple

from django.core.management.base import BaseCommand
from django.db import connections
from django.utils.functional import cached_property
from common_utils.asciitable import NamedtupleTablePrinter


FilterFormat = namedtuple('FilterFormat', ['format', 'name'])


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
		return tuple(FilterFormat(*row) for row in cursor.fetchall())

	def handle(self, *args, **options):
		print('filter_formats')
		print(NamedtupleTablePrinter(self.filter_formats, FilterFormat).render())
