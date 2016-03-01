# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import basename

from easy_thumbnails.files import get_thumbnailer


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
				thumbnailer = get_thumbnailer(attachment.attachment.name)
				options = {'size': (256, 256)}
				attachment_data['width'] = attachment.attachmentimage.width
				attachment_data['height'] = attachment.attachmentimage.height
				attachment_data['thumbnails'] = {
					'standard': thumbnailer.get_thumbnail(options).url
				}
			attachments.append(attachment_data)
		return attachments
