# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template.defaultfilters import filesizeformat


class AttachmentManagementMixin(object):
	def get_attachments_list(self, qs):
		attachments = []
		for attachment in qs:
			attachment_data = {
				'id': attachment.id,
				'url': attachment.attachment.url,
				'size': attachment.size,
				'size_human': filesizeformat(attachment.size)
			}
			if hasattr(attachment, 'attachmentimage'):
				attachment_data['width'] = attachment.attachmentimage.width
				attachment_data['height'] = attachment.attachmentimage.height
				attachment_data['thumbnails'] = {
					'standard': attachment.attachmentimage.attachment_standard.url
				}
			attachments.append(attachment_data)
		return attachments
