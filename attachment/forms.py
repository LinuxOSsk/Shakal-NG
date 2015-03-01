# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.forms.models import modelformset_factory

from .models import UploadSession, TemporaryAttachment, Attachment
from .utils import get_available_size


AttachmentFormSet = modelformset_factory(TemporaryAttachment, can_delete=True, extra=0, fields=())


class TemporaryAttachmentFormMixin(object):
	def __init__(self, *args, **kwargs):
		super(TemporaryAttachmentFormMixin, self).__init__(*args, **kwargs)
		self._attachments = None

	def get_uploadsession(self):
		try:
			session = UploadSession.objects.get(uuid=self.data.get('upload_session', ''))
		except UploadSession.DoesNotExist:
			session = UploadSession()
			session.save()
		self.data['upload_session'] = session.uuid
		return session

	def process_attachments(self):
		self.update_attachment_size()
		self.process_attachment_delete()
		if not hasattr(self, 'security_errors') or not self.security_errors():
			self.process_attachment_upload()
		self.update_attachment_size()

	def process_attachment_delete(self):
		if self.data:
			attachments = self.get_attachments()
			rownum = 0
			while 'form-' + str(rownum) + '-id' in self.data:
				pk = int(self.data['form-' + str(rownum) + '-id'])
				if 'form-' + str(rownum) + '-DELETE' in self.data:
					match = [x for x in attachments if x.pk == pk]
					if match:
						match[0].delete()
				rownum += 1
			self.update_attachment_size()

	def process_attachment_upload(self):
		if not self.files:
			return

		session = self.get_uploadsession()
		try:
			cleaned_file = self.fields['attachment'].clean(self.files['attachment'], self.files['attachment'])

			attachment = TemporaryAttachment(
				session=session,
				attachment=cleaned_file,
				content_type=ContentType.objects.get_for_model(TemporaryAttachment),
				object_id=session.id
			)
			attachment.save()
			self.update_attachment_size()
		except ValidationError:
			return

	def update_attachment_size(self):
		if 'upload_session' in self.data:
			uploaded_size = TemporaryAttachment.objects \
				.filter(session__uuid=self.data['upload_session']) \
				.aggregate(Sum('size'))["size__sum"] or 0
		else:
			uploaded_size = 0
		content_type = ContentType.objects.get_for_model(self.get_model())
		max_size = get_available_size(content_type, uploaded_size)
		self.fields['attachment'].widget.attrs['max_size'] = max_size

	def move_attachments(self, content_object):
		temp_attachments = self.get_attachments()
		for temp_attachment in temp_attachments:
			attachment = Attachment(
				attachment=temp_attachment.attachment.name,
				content_type=ContentType.objects.get_for_model(content_object.__class__),
				object_id=content_object.pk
			)
			attachment.save()
			temp_attachment.delete()

	def get_attachments(self):
		upload_session = UploadSession.objects.filter(uuid=self.data.get('upload_session', ''))
		return TemporaryAttachment.objects.filter(session__in=upload_session).order_by('pk')

	@property
	def attachments(self):
		if self._attachments is None:
			self._attachments = AttachmentFormSet(queryset=self.get_attachments())
		return self._attachments
