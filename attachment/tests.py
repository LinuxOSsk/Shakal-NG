# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

import os
from attachment.models import UploadSession, Attachment, TemporaryAttachment


class AttachmentModelTest(TestCase):
	def setUp(self):
		self.testContentType = ContentType.objects.all()[0]
		self.ct = self.testContentType.model_class()._meta.db_table

	def test_upload_session(self):
		session1 = UploadSession()
		session2 = UploadSession()
		self.assertNotEquals(session1.uuid, session2.uuid)

	def test_available_size(self):
		new_settings = {'ATTACHMENT_MAX_SIZE': -1, 'ATTACHMENT_SIZE_FOR_CONTENT': {self.ct: -1}}
		with self.settings(**new_settings):
			self.assertEqual(Attachment.get_available_size(self.testContentType.pk, 0), -1)

		new_settings['ATTACHMENT_MAX_SIZE'] = 1
		with self.settings(**new_settings):
			self.assertEqual(Attachment.get_available_size(self.testContentType.pk, 0), 1)

		new_settings['ATTACHMENT_MAX_SIZE'] = -1
		new_settings['ATTACHMENT_SIZE_FOR_CONTENT'][self.ct] = 1
		with self.settings(**new_settings):
			self.assertEqual(Attachment.get_available_size(self.testContentType.pk, 0), 1)

	def test_upload_temporary(self):
		file_data = b"0123456789"
		attachment = self.create_temporary_attachment(file_data, "test.txt")
		attachment.save()
		saved_file_name = os.path.join(settings.MEDIA_ROOT, attachment.attachment.name)
		file_readed = open(saved_file_name, 'rb').read()
		self.assertEqual(file_data, file_readed)
		# vymazaný súbor
		attachment.delete()
		with self.assertRaises(IOError):
			open(saved_file_name, 'rb').read()

	def test_upload(self):
		file_data = b"0123456789"
		temp_attachment = self.create_temporary_attachment(file_data, "test.txt")
		temp_attachment.save()
		saved_test_file_name = os.path.join(settings.MEDIA_ROOT, temp_attachment.attachment.name)
		file_readed = open(saved_test_file_name, 'rb').read()
		self.assertEqual(file_data, file_readed)

		test_object = UploadSession()
		test_object.save()

		attachment = Attachment(
			attachment = temp_attachment.attachment.name,
			content_type = ContentType.objects.get_for_model(test_object.__class__),
			object_id = test_object.id
		)
		attachment.save()
		temp_attachment.delete()

		# Test na vymazanie
		with self.assertRaises(IOError):
			open(saved_test_file_name, 'rb').read()

		saved_file_name = os.path.join(settings.MEDIA_ROOT, attachment.attachment.name)
		file_readed = open(saved_file_name, 'rb').read()
		self.assertEqual(file_data, file_readed)

	def create_temporary_attachment(self, file_data, file_name):
		uploaded_file = SimpleUploadedFile("test.txt", file_data)
		session = UploadSession()
		session.save()
		attachment = TemporaryAttachment(
			session = session,
			attachment = uploaded_file,
			content_type = ContentType.objects.get_for_model(TemporaryAttachment),
			object_id = session.id
		)
		return attachment
