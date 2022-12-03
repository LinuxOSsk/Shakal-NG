# -*- coding: utf-8 -*-
# pylint: disable=no-member
import os

from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .fields import AttachmentFieldMultiple
from .forms import AttachmentFormMixin
from .models import UploadSession, Attachment
from .utils import get_available_size
from common_utils import get_meta
from common_utils.tests_common import ProcessFormTestMixin


class AttachmentModelTest(TestCase):
	def setUp(self):
		self.testContentType = ContentType.objects.all()[0]
		self.ct = get_meta(self.testContentType.model_class()).db_table

	def test_upload_session(self):
		session1 = UploadSession()
		session2 = UploadSession()
		self.assertNotEqual(session1.uuid, session2.uuid)

	def create_temporary_attachment(self, name, data):
		uploaded_file = SimpleUploadedFile(name, data)
		session = UploadSession()
		session.save()

		attachment = Attachment(
			attachment=uploaded_file,
			content_type=ContentType.objects.get_for_model(session.__class__),
			object_id=session.id
		)
		return attachment

	def test_paths(self):
		try:
			attachment = self.create_temporary_attachment("test.txt", "")
			attachment.save()
			self.assertEqual(attachment.basename, "test.txt")
			self.assertEqual(attachment.name, "test.txt")
			self.assertEqual(attachment.url.index(settings.MEDIA_URL), 0)
			self.assertEqual(attachment.filename.index(str(settings.MEDIA_ROOT)), 0)
		finally:
			attachment.delete()

	def test_upload(self):
		try:
			file_data = b"0123456789"
			attachment = self.create_temporary_attachment("test.txt", file_data)
			attachment.save()

			saved_file_name = attachment.filename
			file_readed = open(saved_file_name, 'rb').read()
			self.assertEqual(file_data, file_readed)
		finally:
			attachment.delete()

	def test_delete(self):
		try:
			attachment = self.create_temporary_attachment("test.txt", "")
			attachment.save()
			saved_file_name = attachment.filename
			self.assertTrue(os.path.exists(saved_file_name))
		finally:
			attachment.delete()
		self.assertFalse(os.path.exists(saved_file_name))

	def test_replace_file(self):
		try:
			attachment = self.create_temporary_attachment("test.txt", b"A")
			attachment.save()

			file_readed = open(attachment.filename, 'rb').read()
			self.assertEqual(file_readed, b"A")

			attachment.attachment = SimpleUploadedFile("test.txt", b"B")
			attachment.save()

			file_readed = open(attachment.filename, 'rb').read()
			self.assertEqual(file_readed, b"B")
			self.assertEqual(attachment.basename, "test.txt")
		finally:
			attachment.delete()

	def test_upload_final(self):
		try:
			temp_attachment = self.create_temporary_attachment("test.txt", b"A")
			temp_attachment.save()

			attachment = Attachment(
				attachment=temp_attachment.attachment.name,
				content_type=ContentType.objects.get_for_model(Attachment),
				object_id=1
			)
			attachment.save()
			temp_attachment.delete()

			file_readed = open(attachment.filename, 'rb').read()
			self.assertEqual(file_readed, b"A")
		finally:
			temp_attachment.delete_file()
			attachment.delete_file()

	def test_available_size(self):
		ctype = ContentType.objects.get_for_model(UploadSession)
		ctype_table = 'attachment_uploadsession'

		# unlimited
		with self.settings(ATTACHMENT_MAX_SIZE=-1, ATTACHMENT_SIZE_FOR_CONTENT={}):
			self.assertEqual(get_available_size(ctype, 0), -1)

		# base size
		with self.settings(ATTACHMENT_MAX_SIZE=10, ATTACHMENT_SIZE_FOR_CONTENT={}):
			self.assertEqual(get_available_size(ctype, 0), 10)

		# unlimited for content
		with self.settings(ATTACHMENT_MAX_SIZE=10, ATTACHMENT_SIZE_FOR_CONTENT={ctype_table: -1}):
			self.assertEqual(get_available_size(ctype, 0), -1)

		# limited size for content
		with self.settings(ATTACHMENT_MAX_SIZE=-1, ATTACHMENT_SIZE_FOR_CONTENT={ctype_table: 10}):
			self.assertEqual(get_available_size(ctype, 0), 10)

		# limited size for both
		with self.settings(ATTACHMENT_MAX_SIZE=10, ATTACHMENT_SIZE_FOR_CONTENT={ctype_table: 20}):
			self.assertEqual(get_available_size(ctype, 0), 20)

	def test_move_attachment(self):
		try:
			attachment = self.create_temporary_attachment("test.txt", b"A")
			attachment.save()
			session = attachment.content_object

			test_object = UploadSession()
			test_object.save()
			session.move_attachments(test_object)

			attachment = test_object.attachments.all()[0]
		finally:
			attachment.delete()


class AttachmentFormTest(ProcessFormTestMixin, TestCase):
	def test_attachment_field(self):
		field = AttachmentFieldMultiple()
		field.widget.attrs['max_size'] = 2
		field.clean(SimpleUploadedFile("a.txt", b"A")) #OK
		with self.assertRaises(ValidationError):
			field.clean(SimpleUploadedFile("a.txt", b"ABC"))

	def create_attachment_form(self, data=None, files=None):
		class TestForm(AttachmentFormMixin, forms.Form):
			def get_model(self):
				return UploadSession

		return TestForm(data, files)

	def test_simple_upload(self):
		form = self.create_attachment_form({}, {'attachment': SimpleUploadedFile("test.txt", b"A")})

		self.assertTrue(form.is_valid())
		self.assertEqual(len(form.get_attachments()), 1)
		form.get_attachments()[0].delete()

	def test_no_files(self):
		form = self.create_attachment_form({})

		self.assertTrue(form.is_valid())
		self.assertEqual(len(form.get_attachments()), 0)

	def test_validation(self):
		with self.settings(ATTACHMENT_MAX_SIZE=1, ATTACHMENT_SIZE_FOR_CONTENT={}):
			form = self.create_attachment_form({}, {'attachment': SimpleUploadedFile("test.txt", b"AA")})

		self.assertFalse(form.is_valid())
		self.assertEqual(len(form.get_attachments()), 0)

	def test_delete(self):
		form = self.create_attachment_form({}, {'attachment': SimpleUploadedFile("test.txt", b"A")})

		formset = form.attachments
		data = {}
		data.update(self.extract_form_data(form))
		data.update(self.extract_form_data(formset.management_form))
		for attachment_form in formset:
			data.update(self.extract_form_data(attachment_form))
		data['form-0-DELETE'] = '1'

		form = self.create_attachment_form(data)
		form.process_attachments()

		self.assertTrue(form.is_valid())
		self.assertEqual(len(form.get_attachments()), 0)
