# -*- coding: utf-8 -*-
import argparse

from django.core.management import BaseCommand

from ...api import send_weekly, send_mass_email
from common_utils.argparse import add_subparsers


class Command(BaseCommand):
	def add_arguments(self, parser):
		subparsers = add_subparsers(self, parser, description="Subcommand", required=True)
		subparsers.dest = 'subcommand'
		subparsers.add_parser("send_weekly")
		parser = subparsers.add_parser("send_mass")
		parser.add_argument('recipient_list', type=argparse.FileType(mode='r'))
		parser.add_argument('subject_template', type=str)
		parser.add_argument('txt_message_template', type=argparse.FileType(mode='r'))
		parser.add_argument('html_message_template', type=argparse.FileType(mode='r'))

	def handle(self, *args, **options):
		subcommand = options.pop('subcommand')
		return getattr(self, subcommand)(**options)

	def send_weekly(self, **options): # pylint: disable=unused-argument
		send_weekly()

	def send_mass(self, **options):
		recipients = [address.strip() for address in options['recipient_list'] if address.strip()]
		txt_message_template = options['txt_message_template'].read()
		html_message_template = options['html_message_template'].read()
		send_mass_email(
			recipients,
			subject_template=options['subject_template'],
			txt_message_template=txt_message_template,
			html_message_template=html_message_template
		)
