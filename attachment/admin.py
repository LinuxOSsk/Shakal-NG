# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponseBadRequest

from .admin_forms import AttachmentForm
from attachment.models import Attachment, UploadSession
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
	def get_upload_session(self, request, create=False):
		uuid = request.POST.get('upload_session', request.GET.get('upload_session', ''))
		try:
			session = UploadSession.objects.get(uuid=uuid)
		except UploadSession.DoesNotExist:
			if create:
				session = UploadSession()
				session.save()
				request.upload_session = session.uuid
			else:
				return None
		return session

	def attachments_list(self, request, obj):
		is_new = obj is None or isinstance(obj, UploadSession)
		obj = obj or self.get_upload_session(request)
		if obj:
			attachments = (obj.attachments.all()
				.select_related('attachmentimage')
				.order_by('pk'))
		else:
			attachments = Attachment.objects.none()

		data = {
			'list': self.get_attachments_list(attachments),
			'upload_session': obj.uuid if obj and is_new else '',
		}
		return create_json_response(data)

	def attachments_upload(self, request, obj):
		obj = obj or self.get_upload_session(request, create=True)
		if 'attachment' in request.FILES:
			attachment = Attachment(
				attachment=request.FILES['attachment'],
				content_object=obj
			)
			attachment.save()
		return self.attachments_list(request, obj)

	def attachments_delete(self, request, obj):
		obj = obj or self.get_upload_session(request, create=True)
		pk = int(request.POST.get('pk', ''))
		ctype = ContentType.objects.get_for_model(obj)
		attachment = Attachment.objects.get(pk=pk, content_type=ctype, object_id=obj.pk)
		attachment.delete()
		return self.attachments_list(request, obj)

	def changeform_view(self, request, object_id=None, *args, **kwargs):
		if object_id is None:
			obj = None
		else:
			obj = self.get_object(request, unquote(object_id))
		attachment_action = request.POST.get('attachment_action', request.GET.get('attachment_action', ''))
		if attachment_action == 'list' and request.method == 'GET':
			return self.attachments_list(request, obj)
		elif attachment_action == 'upload' and request.method == 'POST':
			return self.attachments_upload(request, obj)
		elif attachment_action == 'delete' and request.method == 'POST':
			return self.attachments_delete(request, obj)
		elif attachment_action == '':
			return super(AttachmentAdminMixin, self).changeform_view(request, object_id, *args, **kwargs)
		else:
			return HttpResponseBadRequest()

	def save_model(self, request, obj, form, change):
		super(AttachmentAdminMixin, self).save_model(request, obj, form, change)
		if not change:
			session = self.get_upload_session(request, create=True)
			if session:
				session.move_attachments(obj)


admin.site.register(Attachment, AttachmentAdmin)
