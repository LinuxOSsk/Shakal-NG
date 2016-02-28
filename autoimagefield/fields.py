# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from functools import partial

from django.conf import settings
from django.db.models import signals
from easy_thumbnails.fields import ThumbnailerImageField


class AutoImageFieldMixin(object):
	def generate_filename(self, instance, filename):
		if instance.pk:
			return os.path.join(self.get_directory_name(), "{0:02x}".format(instance.pk % 256), str(instance.pk), self.get_filename(filename))
		else:
			return super(AutoImageFieldMixin, self).generate_filename(instance, filename)

	def __get_paths(self, instance, field):
		new_filename = None
		try:
			src = os.path.abspath(field.path)
			ext = os.path.splitext(src)[1].lower().replace('jpg', 'jpeg')
			new_filename = self.generate_filename(instance, "{0}_{1}{2}".format(self.name, instance.pk, ext))
			dest = os.path.abspath(os.path.join(settings.MEDIA_ROOT, new_filename))
		except ValueError:
			src = None
			dest = None
		return (src, dest, new_filename)

	def _rename_image(self, name, instance, **kwargs):
		field = getattr(instance, name)

		old_file = getattr(instance, name + '_old')
		if old_file:
			old_file.delete_thumbnails()

		src, dest, new_filename = self.__get_paths(instance, field)
		if src and src != dest and os.path.exists(src):
			if not os.path.exists(os.path.dirname(dest)):
				os.makedirs(os.path.dirname(dest))
			os.rename(src, dest)
			setattr(instance, name, new_filename)
			instance.save()

		if old_file and old_file != new_filename and os.path.exists(field.storage.path(old_file)):
			field.storage.delete(old_file)
			self.__clean_dir(os.path.dirname(field.storage.path(old_file)))

	def _delete_image(self, name, instance, **kwargs):
		field = getattr(instance, name)
		field.delete_thumbnails()
		field.storage.delete(field.path)
		if field:
			self.__clean_dir(os.path.dirname(field.storage.path(field)))

	def _store_old_value(self, name, instance, **kwargs):
		if instance.pk:
			setattr(instance, name + '_old', getattr(instance, name))
		else:
			setattr(instance, name + '_old', None)

	def __clean_dir(self, path):
		path = os.path.abspath(path)
		topdir = os.path.abspath(os.path.join(settings.MEDIA_ROOT, self.get_directory_name()))
		if not path.startswith(topdir) or path == topdir:
			return
		# remove empty directory
		try:
			os.rmdir(path)
		except OSError:
			return
		updir = os.path.join(*os.path.split(path)[:-1])
		if updir.startswith(topdir) and updir != topdir:
			self.__clean_dir(updir)


class AutoImageField(AutoImageFieldMixin, ThumbnailerImageField):
	def contribute_to_class(self, cls, name):
		super(AutoImageField, self).contribute_to_class(cls, name)

		signals.post_init.connect(partial(self._store_old_value, name=name), sender=cls, weak=False)
		signals.post_save.connect(partial(self._rename_image, name=name), sender=cls, weak=False)
		signals.post_delete.connect(partial(self._delete_image, name=name), sender=cls, weak=False)
