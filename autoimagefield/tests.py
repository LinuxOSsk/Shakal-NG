# -*- coding: utf-8 -*-
import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from autoimagefield.utils import thumbnail as generate_thumbnail
from common_utils.tests_common import create_image
from tests.models import ImageFieldModel


class AutoImageFieldTest(TestCase):
	def create_image_instance(self, **kwargs):
		image = create_image(**kwargs)

		instance = ImageFieldModel()
		instance.image = SimpleUploadedFile(image.name, image.read())
		instance.save()
		return instance

	def destroy_image_instance(self, instance):
		instance.delete()

	def test_instance_life(self):
		instance = self.create_image_instance()
		path = instance.image.path
		self.assertTrue(os.path.exists(path))
		self.destroy_image_instance(instance)
		self.assertFalse(os.path.exists(path))

	def test_resize(self):
		from PIL import Image
		instance = self.create_image_instance(size=(128, 128))
		im = Image.open(instance.image.path)
		self.assertEqual(im.size, (64, 64))
		self.destroy_image_instance(instance)

	def test_rename(self):
		instance = self.create_image_instance(size=(128, 128))
		path1 = instance.image.path
		thumbnail = generate_thumbnail(instance.image, size=(32, 32))
		path1_thumbnail = thumbnail.path
		path1_thumbnail_url = thumbnail.url
		path1_thumbnail_size = thumbnail.size
		instance.pk = 2
		instance.save()
		instance = ImageFieldModel.objects.get(pk=instance.pk)
		path2 = instance.image.path
		thumbnail = generate_thumbnail(instance.image, size=(32, 32))
		path2_thumbnail = thumbnail.path
		path2_thumbnail_url = thumbnail.url
		path2_thumbnail_size = thumbnail.size

		self.assertNotEqual(path1, path2)
		self.assertNotEqual(path1_thumbnail_url, path2_thumbnail_url)
		self.assertEqual(path1_thumbnail_size, path2_thumbnail_size)
		self.assertFalse(os.path.exists(path1))
		self.assertFalse(os.path.exists(path1_thumbnail))
		self.assertTrue(os.path.exists(path2))
		self.assertTrue(os.path.exists(path2_thumbnail))

		self.destroy_image_instance(instance)

	def test_reupload(self):
		instance = self.create_image_instance(size=(128, 128))
		path1 = instance.image.path
		path1_thumbnail = generate_thumbnail(instance.image, size=(32, 32)).path

		instance = ImageFieldModel.objects.get(pk=instance.pk)
		image = create_image(size=(128, 128), filetype='jpeg', basename='new')
		instance.image = SimpleUploadedFile(image.name, image.read())
		instance.save()

		path2 = instance.image.path
		path2_thumbnail = generate_thumbnail(instance.image, size=(32, 32)).path

		self.assertNotEqual(path1, path2)
		self.assertNotEqual(path1_thumbnail, path2_thumbnail)
		self.assertFalse(os.path.exists(path1))
		self.assertFalse(os.path.exists(path1_thumbnail))
		self.assertTrue(os.path.exists(path2))
		self.assertTrue(os.path.exists(path2_thumbnail))

		self.destroy_image_instance(instance)

	def test_remove_image(self):
		instance = self.create_image_instance(size=(128, 128))
		path1 = instance.image.path
		instance.image = None
		instance.save()
		self.assertFalse(os.path.exists(path1))
		self.destroy_image_instance(instance)
