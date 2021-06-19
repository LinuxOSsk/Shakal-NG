# -*- coding: utf-8 -*-
from os.path import basename

from autoimagefield.utils import thumbnail


class AttachmentManagementMixin(object):
	def get_attachments_list(self, qs):
		attachments = []
		for attachment in qs:
			attachment_data = {
				'id': attachment.id,
				'url': attachment.attachment.url,
				'name': basename(attachment.attachment.name),
				'filesize': attachment.size,
			}
			if hasattr(attachment, 'attachmentimage'):
				thumb = thumbnail(attachment.attachment, size=(256, 256))
				if thumb:
					attachment_data['width'] = attachment.attachmentimage.width
					attachment_data['height'] = attachment.attachmentimage.height
					attachment_data['thumbnails'] = {
						'standard': thumb.url
					}
			attachments.append(attachment_data)
		return attachments
