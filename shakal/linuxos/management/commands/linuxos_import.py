# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import connections

class Command(BaseCommand):
	args = ''
	help = 'Import data from LinuxOS'

	def handle(self, *args, **kwargs):
		self.cursor = connections["linuxos"].cursor()
		self.importArticles()

	def importArticles(self):
		self.cursor.execute("SELECT * FROM clanky")

