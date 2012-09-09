# -*- coding: utf-8 -*-

from attachment.models import TemporaryAttachment
import datetime
from django.core.management.base import BaseCommand

class Command(BaseCommand):
	args = ''
	help = 'Cron'

	def __init__(self, *args, **kwargs):
		super(Command, self).__init__(*args, **kwargs)

	def handle(self, *args, **kwargs):
		now = datetime.datetime.now()
		old_date = now - datetime.timedelta(days = 1)
		old_attachments = TemporaryAttachment.objects.filter(created__lt = old_date)[:]
		for old_attachment in old_attachments:
			old_attachment.delete()
