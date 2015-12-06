# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.forms.models import modelformset_factory

from .fields import AttachmentField
from .models import UploadSession, Attachment
from .utils import get_available_size


AttachmentFormSet = modelformset_factory(Attachment, can_delete=True, extra=0, fields=())


class TemporaryAttachmentFormMixin(forms.BaseForm):
	def __init__(self, *args, **kwargs):
		super(TemporaryAttachmentFormMixin, self).__init__(*args, **kwargs)
		self._attachments = None
		self.fields['attachment'] = AttachmentField(label='Príloha', required=False)
		self.fields['upload_session'] = forms.CharField(widget=forms.HiddenInput, required=False)
		self.process_attachments()

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

			attachment = Attachment(
				attachment=cleaned_file,
				content_object=session
			)
			attachment.save()
			self.update_attachment_size()
		except ValidationError:
			return

	def update_attachment_size(self):
		if 'upload_session' in self.data:
			try:
				upload_session = (UploadSession.objects
					.get(uuid=self.data['upload_session']))
				uploaded_size = (upload_session.attachments
					.aggregate(Sum('size'))["size__sum"]) or 0
			except UploadSession.DoesNotExist:
				uploaded_size = 0
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
		try:
			upload_session = (UploadSession.objects
				.get(uuid=self.data.get('upload_session', '')))
			return (upload_session.attachments
				.order_by('pk'))
		except UploadSession.DoesNotExist:
			return Attachment.objects.none()

	@property
	def attachments(self):
		if self._attachments is None:
			self._attachments = AttachmentFormSet(queryset=self.get_attachments())
		return self._attachments


class AttachmentFormMixin(object):
	def __init__(self, *args, **kwargs):
		self.content_object = kwargs.pop('content_object')
		super(AttachmentFormMixin, self).__init__(*args, **kwargs)
		self._attachments = None

	@property
	def content_type(self):
		return ContentType.objects.get_for_model(self.content_object.__class__)

	@property
	def object_id(self):
		return self.content_object.pk

	def process_attachments(self):
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

		try:
			cleaned_file = self.fields['attachment'].clean(self.files['attachment'], self.files['attachment'])

			attachment = Attachment(
				attachment=cleaned_file,
				content_type=self.content_type,
				object_id=self.object_id
			)
			attachment.save()
			self.update_attachment_size()
		except ValidationError:
			return

	def update_attachment_size(self):
		uploaded_size = self.get_attachments().aggregate(Sum('size'))["size__sum"] or 0
		max_size = get_available_size(self.content_type, uploaded_size)
		self.fields['attachment'].widget.attrs['max_size'] = max_size

	def get_attachments(self):
		return Attachment.objects.\
			filter(content_type=self.content_type, object_id=self.object_id).\
			order_by('pk')

	@property
	def attachments(self):
		if self._attachments is None:
			self._attachments = AttachmentFormSet(queryset=self.get_attachments())
		return self._attachments
