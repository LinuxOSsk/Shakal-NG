# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.encoding import smart_unicode

from .fields import AttachmentField
from .models import UploadSession, Attachment, TemporaryAttachment
from .utils import get_available_size


class AttachmentModelTest(TestCase):
	def setUp(self):
		self.testContentType = ContentType.objects.all()[0]
		self.ct = self.testContentType.model_class()._meta.db_table

	def test_upload_session(self):
		session1 = UploadSession()
		session2 = UploadSession()
		self.assertNotEqual(session1.uuid, session2.uuid)

	def create_temporary_attachment(self, name, data):
		uploaded_file = SimpleUploadedFile(name, data)
		session = UploadSession()
		session.save()

		attachment = TemporaryAttachment(
			session = session,
			attachment = uploaded_file,
			content_type = ContentType.objects.get_for_model(TemporaryAttachment),
			object_id = session.id
		)
		return attachment

	def test_paths(self):
		try:
			attachment = self.create_temporary_attachment("test.txt", "")
			attachment.save()
			self.assertEqual(attachment.basename, "test.txt")
			self.assertEqual(attachment.name, "test.txt")
			self.assertEqual(attachment.url.index(settings.MEDIA_URL), 0)
			self.assertEqual(attachment.filename.index(settings.MEDIA_ROOT), 0)
			self.assertEqual(smart_unicode(attachment), attachment.attachment.name)
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
			self.assertEqual(file_readed, "A")

			attachment.attachment = SimpleUploadedFile("test.txt", b"B")
			attachment.save()

			file_readed = open(attachment.filename, 'rb').read()
			self.assertEqual(file_readed, "B")
			self.assertEqual(attachment.basename, "test.txt")
		finally:
			attachment.delete()

	def test_upload_final(self):
		try:
			temp_attachment = self.create_temporary_attachment("test.txt", b"A")
			temp_attachment.save()

			attachment = Attachment(
				attachment = temp_attachment.attachment.name,
				content_type = ContentType.objects.get_for_model(UploadSession),
				object_id = 1
			)
			attachment.save()
			temp_attachment.delete()

			file_readed = open(attachment.filename, 'rb').read()
			self.assertEqual(file_readed, "A")
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

	def test_oversize(self):
		with self.settings(ATTACHMENT_MAX_SIZE=-1, ATTACHMENT_SIZE_FOR_CONTENT={'attachment_temporaryattachment': 2}):
			try:
				temp_attachment = self.create_temporary_attachment("test.txt", b"ABCD")
				with self.assertRaises(ValidationError):
					temp_attachment.size = temp_attachment.attachment.size
					temp_attachment.full_clean()
			finally:
				temp_attachment.delete_file()

			try:
				temp_attachment = self.create_temporary_attachment("test.txt", b"A")
				temp_attachment.size = temp_attachment.attachment.size
				temp_attachment.full_clean()
			finally:
				temp_attachment.delete_file()


class AttachmentFormTest(TestCase):
	def test_attachment_field(self):
		field = AttachmentField()
		field.widget.attrs['max_size'] = 2
		field.clean(SimpleUploadedFile("a.txt", "A")) #OK
		with self.assertRaises(ValidationError):
			field.clean(SimpleUploadedFile("a.txt", "ABC"))

	def test_render(self):
		field = AttachmentField()
		field.widget.attrs['max_size'] = 2
		field.widget.render("name", "")
