# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.contrib.contenttypes.admin import GenericTabularInline
from django.http import HttpResponse, HttpResponseBadRequest

from .admin_forms import AttachmentForm
from .models import Attachment


class AttachmentInline(GenericTabularInline):
	model = Attachment
	form = AttachmentForm

	template = 'admin/edit_inline/attachments.html'

	verbose_name = 'príloha'
	verbose_name_plural = 'prílohy'

	ct_field = 'content_type'
	ct_fk_field = 'object_id'

	fields = ('attachment',)

	can_delete = True
	extra = 3

	def get_queryset(self, request):
		return super(AttachmentInline, self).get_queryset(request).select_related('attachmentimage')


class AttachmentAdmin(admin.ModelAdmin):
	exclude = ('size', )


class AttachmentAdminMixin(object):
	def attachments_list(self, request, object_id):
		obj = self.get_object(request, unquote(object_id))
		print(obj)
		return HttpResponse('')

	def change_view(self, request, object_id, **kwargs):
		attachment_action = request.POST.get('attachment-action', request.GET.get('attachment-action', ''))
		if attachment_action == 'list' and request.method == 'GET':
			return self.attachments_list(request, object_id)
		elif attachment_action == '':
			return super(AttachmentAdminMixin, self).change_view(request, object_id, **kwargs)
		else:
			return HttpResponseBadRequest()


admin.site.register(Attachment, AttachmentAdmin)
