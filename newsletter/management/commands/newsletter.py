# -*- coding: utf-8 -*-
from django.core.management import BaseCommand

from common_utils.argparse import add_subparsers


class Command(BaseCommand):
	def add_arguments(self, parser):
		subparsers = add_subparsers(self, parser, description="Subcommand", required=True)
		subparsers.dest = 'subcommand'
		subparsers.add_parser("send_weekly")

	def handle(self, *args, **options):
		subcommand = options.pop('subcommand')
		return getattr(self, subcommand)(**options)

	def send_weekly(self, **options):
		pass
