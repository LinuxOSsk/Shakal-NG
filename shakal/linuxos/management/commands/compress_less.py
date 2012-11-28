# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from subprocess import call
import os
import sys

class Command(BaseCommand):
	args = ''
	help = 'Cron'

	def __init__(self, *args, **kwargs):
		super(Command, self).__init__(*args, **kwargs)

	def handle(self, *args, **kwargs):
		root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
		input_path = os.path.join(root_path, 'static', 'desktop', 'default', 'base.less')
		output_path = os.path.join(root_path, 'static', 'desktop', 'default', 'base.css')
		call(['lessc', input_path, '-x', '--yui-compress', '--02'], stdout = open(output_path, 'w'), stderr = sys.stderr)
