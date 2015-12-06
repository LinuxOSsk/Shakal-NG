# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponseBadRequest

from .admin_forms import AttachmentForm
from attachment.models import Attachment
from attachment.views import AttachmentManagementMixin
from common_utils.json_utils import create_json_response


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


class AttachmentAdminMixin(AttachmentManagementMixin):
	def attachments_list(self, obj):
		if obj is None:
			return create_json_response([])
		attachments = (obj.attachments.all()
			.order_by('pk')
			.select_related('attachmentimage'))
		return create_json_response(self.get_attachments_list(attachments))

	def attachments_upload(self, request, obj):
		if 'attachment' in request.FILES:
			attachment = Attachment(
				attachment=request.FILES['attachment'],
				content_type=ContentType.objects.get_for_model(obj.__class__),
				object_id=obj.pk
			)
			attachment.save()
		return self.attachments_list(obj)

	def attachments_delete(self, request, obj):
		pk = int(request.POST.get('pk', ''))
		content_type = ContentType.objects.get_for_model(obj.__class__)
		attachment = Attachment.objects.get(pk=pk, content_type_id=content_type, object_id=obj.pk)
		attachment.delete()
		return self.attachments_list(obj)

	def changeform_view(self, request, object_id=None, *args, **kwargs):
		if object_id is None:
			obj = None
		else:
			obj = self.get_object(request, unquote(object_id))
		attachment_action = request.POST.get('attachment-action', request.GET.get('attachment-action', ''))
		if attachment_action == 'list' and request.method == 'GET':
			return self.attachments_list(obj)
		elif attachment_action == 'upload' and request.method == 'POST':
			return self.attachments_upload(request, obj)
		elif attachment_action == 'delete' and request.method == 'POST':
			return self.attachments_delete(request, obj)
		elif attachment_action == '':
			return super(AttachmentAdminMixin, self).changeform_view(request, object_id, *args, **kwargs)
		else:
			return HttpResponseBadRequest()


admin.site.register(Attachment, AttachmentAdmin)
