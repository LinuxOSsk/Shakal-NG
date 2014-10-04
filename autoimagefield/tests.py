# -*- coding: utf-8 -*-
import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .fields import AutoImageField
from common_utils.tests_common import CreateModelsMixin, TestModel, create_image


class ImageFieldModel(TestModel):
	image = AutoImageField(upload_to='test/thumbnails', size=(64, 64), thumbnail={'thumbnail': (32, 32)}, blank=True, null=True)

	def __unicode__(self):
		return self.image.path


class AutoImageFieldTest(CreateModelsMixin, TestCase):
	temporary_models = (ImageFieldModel,)

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
		self.assertEquals(im.size, (64, 64))
		self.destroy_image_instance(instance)

	def test_rename(self):
		instance = self.create_image_instance(size=(128, 128))
		path1 = instance.image.path
		thumbnail = instance.image_thumbnail #pylint: disable=no-member
		path1_thumbnail = thumbnail.path
		path1_thumbnail_url = thumbnail.url
		path1_thumbnail_size = thumbnail.size
		instance.pk = 2
		instance.save()
		instance = ImageFieldModel.objects.get(pk=instance.pk)
		path2 = instance.image.path
		thumbnail = instance.image_thumbnail #pylint: disable=no-member
		path2_thumbnail = thumbnail.path
		path2_thumbnail_url = thumbnail.url
		path2_thumbnail_size = thumbnail.size

		self.assertNotEquals(path1, path2)
		self.assertNotEquals(path1_thumbnail_url, path2_thumbnail_url)
		self.assertEquals(path1_thumbnail_size, path2_thumbnail_size)
		self.assertFalse(os.path.exists(path1))
		self.assertFalse(os.path.exists(path1_thumbnail))
		self.assertTrue(os.path.exists(path2))
		self.assertTrue(os.path.exists(path2_thumbnail))

		self.destroy_image_instance(instance)

	def test_reupload(self):
		instance = self.create_image_instance(size=(128, 128))
		path1 = instance.image.path
		path1_thumbnail = instance.image_thumbnail.path #pylint: disable=no-member

		instance = ImageFieldModel.objects.get(pk=instance.pk)
		image = create_image(size=(128, 128), filetype='jpeg', basename='new')
		instance.image = SimpleUploadedFile(image.name, image.read())
		instance.save()

		path2 = instance.image.path
		path2_thumbnail = instance.image_thumbnail.path #pylint: disable=no-member

		self.assertNotEquals(path1, path2)
		self.assertNotEquals(path1_thumbnail, path2_thumbnail)
		self.assertFalse(os.path.exists(path1))
		self.assertFalse(os.path.exists(path1_thumbnail))
		self.assertTrue(os.path.exists(path2))
		self.assertTrue(os.path.exists(path2_thumbnail))

		self.destroy_image_instance(instance)

	def test_blank(self):
		instance = ImageFieldModel()
		instance.save()
		self.assertIsNone(instance.image_thumbnail) #pylint: disable=no-member
		self.destroy_image_instance(instance)

	def test_remove_image(self):
		instance = self.create_image_instance(size=(128, 128))
		path1 = instance.image.path
		instance.image = None
		instance.save()
		self.assertFalse(os.path.exists(path1))
		self.destroy_image_instance(instance)

	def test_removed_image(self):
		instance = self.create_image_instance(size=(128, 128))
		os.remove(instance.image.path)
		instance = ImageFieldModel.objects.get(pk=instance.pk)
		self.assertIsNone(instance.image_thumbnail)
