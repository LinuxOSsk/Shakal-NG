# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from django.utils import timezone

from attachment.models import TemporaryAttachment


def delete_old_attachments():
	old_attachments = TemporaryAttachment.objects.filter(created__lt=timezone.now() - timedelta(1))
	for old_attachment in old_attachments:
		old_attachment.delete()
