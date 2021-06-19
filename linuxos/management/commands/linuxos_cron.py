# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from ...cron_tasks import delete_old_attachments, update_user_ratings, delete_old_events, fix_duplicate_headers


class Command(BaseCommand):
	args = ''
	help = 'Cron'

	def __init__(self, *args, **kwargs):
		super(Command, self).__init__(*args, **kwargs)

	def handle(self, *args, **kwargs):
		delete_old_attachments()
		delete_old_events()
		update_user_ratings()
		fix_duplicate_headers()
