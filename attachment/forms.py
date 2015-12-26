# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.forms.models import modelformset_factory

from .fields import AttachmentFieldMultiple, get_file_list
from .models import UploadSession, Attachment
from .utils import get_available_size


AttachmentFormSet = modelformset_factory(Attachment, can_delete=True, extra=0, fields=())


class AttachmentFormMixin(forms.BaseForm):
	def __init__(self, *args, **kwargs):
		self.content_object = kwargs.pop('content_object', None)
		super(AttachmentFormMixin, self).__init__(*args, **kwargs)
		self._attachments = None

		if self.content_object is None:
			self.fields['attachment'] = AttachmentFieldMultiple(label='Príloha', required=False)
			self.fields['upload_session'] = forms.CharField(widget=forms.HiddenInput, required=False)
			self.content_object = self.get_uploadsession()
		self.process_attachments()

	def get_uploadsession(self, create=False):
		try:
			session = UploadSession.objects.get(uuid=self.data.get('upload_session', ''))
		except UploadSession.DoesNotExist:
			if not create:
				return None
			session = UploadSession()
			session.save()
		self.data['upload_session'] = session.uuid
		return session

	def process_attachments(self):
		self.process_attachment_delete()
		self.update_attachment_size()
		if not hasattr(self, 'security_errors') or not self.security_errors():
			self.process_attachment_upload()
			self.update_attachment_size()

	@property
	def content_type(self):
		return ContentType.objects.get_for_model(self.content_object.__class__)

	@property
	def object_id(self):
		return self.content_object.pk

	@property
	def attachments(self):
		if self._attachments is None:
			self._attachments = AttachmentFormSet(queryset=self.get_attachments())
		return self._attachments

	def get_attachments(self):
		if self.content_object:
			return (Attachment.objects
				.filter(content_type=self.content_type, object_id=self.object_id)
				.order_by('pk'))
		else:
			return Attachment.objects.none()

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

	def process_attachment_upload(self):
		if not self.files:
			return

		if not self.content_object:
			self.content_object = self.get_uploadsession(create=True)

		try:
			cleaned_files = self.fields['attachment'].clean(get_file_list(self.files, 'attachment'))

			if cleaned_files:
				for cleaned_file in cleaned_files:
					if cleaned_file:
						attachment = Attachment(
							attachment=cleaned_file,
							content_object=self.content_object
						)
						attachment.save()
		except ValidationError:
			return

	def get_model(self):
		if self.content_object:
			return self.content_object.__class__
		else:
			return UploadSession

	def update_attachment_size(self):
		uploaded_size = self.get_attachments().aggregate(Sum('size'))["size__sum"] or 0
		content_type = ContentType.objects.get_for_model(self.get_model())
		max_size = get_available_size(content_type, uploaded_size)
		self.fields['attachment'].widget.attrs['max_size'] = max_size

	def move_attachments(self, content_object):
		if self.content_object:
			self.content_object.move_attachments(content_object)
