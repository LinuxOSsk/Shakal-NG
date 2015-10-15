# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.translation import ugettext_lazy as _

from attachment.models import Attachment


class AttachmentInline(GenericStackedInline):
	model = Attachment
	verbose_name = _('attachment')
	verbose_name_plural = _('attachments')
	ct_field = 'content_type'
	ct_fk_field = 'object_id'
	exclude = ('size', )
	can_delete = True
	template = "admin/edit_inline/attachments.html"

	def get_queryset(self, request):
		return super(AttachmentInline, self).get_queryset(request).select_related('attachmentimage')


class AttachmentAdmin(admin.ModelAdmin):
	exclude = ('size', )


admin.site.register(Attachment, AttachmentAdmin)
