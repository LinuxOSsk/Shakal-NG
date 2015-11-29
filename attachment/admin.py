# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from attachment.models import Attachment


class AttachmentInline(GenericTabularInline):
	model = Attachment
	verbose_name = 'príloha'
	verbose_name_plural = 'prílohy'
	ct_field = 'content_type'
	ct_fk_field = 'object_id'
	exclude = ('size', )
	can_delete = True
	template = 'admin/edit_inline/attachments.html'
	readonly_fields = ('attachment',)
	extra = 0

	def get_queryset(self, request):
		return super(AttachmentInline, self).get_queryset(request).select_related('attachmentimage')


class AttachmentAdmin(admin.ModelAdmin):
	exclude = ('size', )


admin.site.register(Attachment, AttachmentAdmin)
