# -*- coding: utf-8 -*-

from attachment.models import UploadSession, TemporaryAttachment, Attachment
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.forms.models import modelformset_factory


class AttachmentForm(forms.Form):
	pass


AttachmentFormset = modelformset_factory(TemporaryAttachment, can_delete = True, extra = 0, fields = ())


class AttachmentFormMixin:
	def process_attachments(self):
		self.process_attachment_delete()
		if not self.security_errors():
			self.process_attachment_upload()

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
		self.set_attachment_size()

	def process_attachment_upload(self):
		print(self.data)
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
			self.set_attachment_size()
		except:
			return

	def set_attachment_size(self):
		try:
			uploaded_size = TemporaryAttachment.objects
			uploaded_size = uploaded_size.filter(session__uuid = self.data['upload_session'])
			uploaded_size = uploaded_size.aggregate(Sum('size'))["size__sum"]
		except KeyError:
			uploaded_size = 0
		if uploaded_size is None:
			uploaded_size = 0
		self.fields['attachment'].widget.attrs['max_size'] = TemporaryAttachment.get_available_size(ContentType.objects.get_for_model(self.get_model()), uploaded_size)

	def move_attachments(self, content_object):
		temp_attachments = self.get_attachments()
		if not temp_attachments:
			return
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
				return TemporaryAttachment.objects.filter(session = session)
			except UploadSession.DoesNotExist:
				return []
		else:
			return []

	@property
	def attachments(self):
		if not hasattr(self, 'attachments_formset'):
			self.attachments_formset = AttachmentFormset(queryset = self.get_attachments())
		return self.attachments_formset
