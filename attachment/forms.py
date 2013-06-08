# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.forms.models import modelformset_factory

from attachment.models import UploadSession, TemporaryAttachment, Attachment


AttachmentFormset = modelformset_factory(TemporaryAttachment, can_delete = True, extra = 0, fields = ())


class AttachmentFormMixin:
	def process_attachments(self):
		self.process_attachment_delete()
		if not self.security_errors():
			self.process_attachment_upload()
		self.update_attachment_size()

	def process_attachment_delete(self):
		if self.data:
			attachments = self.get_attachments()
			rownum = 0
			while 'form-' + str(rownum) + '-id' in self.data:
				pk = int(self.data['form-' + str(rownum) + '-id'])
				if 'form-' + str(rownum) + '-DELETE' in self.data:
					match = filter(lambda x: x.pk == pk, attachments)
					if match:
						match[0].delete()
				rownum += 1
			self.update_attachment_size()

	def process_attachment_upload(self):
		try:
			session = UploadSession.objects.get(uuid = self.data['upload_session'])
		except UploadSession.DoesNotExist:
			if self.files:
				session = UploadSession()
				session.save()
		except KeyError:
			return

		if not self.files:
			return
		self.data['upload_session'] = session.uuid

		try:
			cleaned_file = self.fields['attachment'].clean(self.files['attachment'], self.files['attachment'])

			attachment = TemporaryAttachment(
				session = session,
				attachment = cleaned_file,
				content_type = ContentType.objects.get_for_model(TemporaryAttachment),
				object_id = session.id
			)
			attachment.save()
			self.update_attachment_size()
		except ValidationError:
			return

	def update_attachment_size(self):
		if 'upload_session' in self.data:
			uploaded_size = TemporaryAttachment.objects \
				.filter(session__uuid = self.data['upload_session']) \
				.aggregate(Sum('size'))["size__sum"] or 0
		else:
			uploaded_size = 0
		content_type = ContentType.objects.get_for_model(self.get_model())
		max_size = TemporaryAttachment.get_available_size(content_type, uploaded_size)
		self.fields['attachment'].widget.attrs['max_size'] = max_size

	def move_attachments(self, content_object):
		temp_attachments = self.get_attachments()
		for temp_attachment in temp_attachments:
			attachment = Attachment(
				attachment = temp_attachment.attachment.name,
				content_type = ContentType.objects.get_for_model(content_object.__class__),
				object_id = content_object.pk
			)
			attachment.save()
			temp_attachment.delete()

	def get_attachments(self):
		if self.data and 'upload_session' in self.data:
			try:
				session = UploadSession.objects.get(uuid = self.data['upload_session'])
				return TemporaryAttachment.objects.filter(session = session).order_by('pk')
			except UploadSession.DoesNotExist:
				return []
		else:
			return []

	@property
	def attachments(self):
		if not hasattr(self, '_attachments'):
			self._attachments = AttachmentFormset(queryset = self.get_attachments())
		return self._attachments
