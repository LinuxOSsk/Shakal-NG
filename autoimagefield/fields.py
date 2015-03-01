# -*- coding: utf-8 -*-
import os
import shutil

from django.conf import settings
from django.db.models import signals
from django.db.models.fields.files import ImageField


class ThumbnailField(object):
	"""
	Inštancia sa pužíva na prístup k náhľadom
	"""
	def __init__(self, field, filename=None, size=None):
		self.filename = filename
		self.field = field
		self.thumbnail_size = size

	def _initialize_file(self):
		dest_filename = self.field.storage.path(self.filename)
		if os.path.exists(dest_filename):
			return

		source_filename = self.field.storage.path(str(self.field))
		# Kópia a resize obrázku
		shutil.copy(source_filename, dest_filename)
		AutoImageField.resize_image(dest_filename, self.thumbnail_size)

	def _get_path(self):
		self._initialize_file()
		return self.field.storage.path(self.filename)
	path = property(_get_path)

	def _get_url(self):
		self._initialize_file()
		return self.field.storage.url(self.filename)
	url = property(_get_url)

	def _get_size(self):
		self._initialize_file()
		return self.field.storage.size(self.filename)
	size = property(_get_size)


class AutoImageFieldMixin(object):
	WIDTH, HEIGHT = 0, 1

	@staticmethod
	def resize_image(filename, size):
		from PIL import Image
		img = Image.open(filename)
		if img.size[AutoImageField.WIDTH] > size[AutoImageField.WIDTH] or img.size[AutoImageField.HEIGHT] > size[AutoImageField.HEIGHT]:
			img.thumbnail((size[AutoImageField.WIDTH], size[AutoImageField.HEIGHT]), Image.ANTIALIAS)
		img.save(filename, optimize=1)

	def get_object_pk(self, instance):
		return instance.pk

	def generate_filename(self, instance, filename):
		if self.get_object_pk(instance):
			return os.path.join(self.get_directory_name(), "{0:02x}".format(self.get_object_pk(instance) % 256), str(self.get_object_pk(instance)), self.get_filename(filename))
		else:
			return super(AutoImageFieldMixin, self).generate_filename(instance, filename)

	def __perform_rename_file(self, src, dest):
		if not os.path.exists(os.path.dirname(dest)):
			os.makedirs(os.path.dirname(dest))
		os.rename(src, dest)

		# Presun / kópia náhľadov
		for label in self.thumbnail:
			old_tmb = AutoImageField.get_thumbnail_filename(src, label)
			new_tmb = AutoImageField.get_thumbnail_filename(dest, label)
			if os.path.exists(old_tmb):
				os.rename(old_tmb, new_tmb)

	def __perform_remove_file(self, path):
		if os.path.exists(path):
			os.remove(path)

		for label in self.thumbnail:
			tmb_filename = AutoImageField.get_thumbnail_filename(path, label)
			if os.path.exists(tmb_filename):
				os.remove(tmb_filename)

	def __get_paths(self, instance):
		new_file = None
		try:
			# Pôvodná adresa
			src = os.path.abspath(getattr(instance, self.name).path)
			ext = os.path.splitext(src)[1].lower().replace('jpg', 'jpeg')
			new_file = self.generate_filename(instance, "{0}_{1}{2}".format(self.name, instance.pk, ext))
			dest = os.path.abspath(os.path.join(settings.MEDIA_ROOT, new_file))
		except ValueError:
			src = None
			dest = None
		return (src, dest, new_file)

	def _rename_image(self, instance, **kwargs):
		field = getattr(instance, self.name)
		src, dest, new_file = self.__get_paths(instance)

		if src and src != dest and os.path.exists(src):
			self.__perform_rename_file(src, dest)
			setattr(instance, self.name, new_file)
			instance.save()

		# Ak je definovaná veľkosť škálujeme obrázok
		if src:
			if self.size:
				self.resize_image(dest, self.size)

		old = getattr(instance, self.name + '_old', None)
		if old and old != new_file and os.path.exists(field.storage.path(old)):
			self.__perform_remove_file(field.storage.path(old))
			instance.old = new_file
			self.__clean_dir(os.path.dirname(field.storage.path(old)))
		if src:
			self.__clean_dir(os.path.dirname(src))

		self._add_old_instance(instance, **kwargs)

	def __clean_dir(self, path):
		path = os.path.abspath(path)
		topdir = os.path.abspath(os.path.join(settings.MEDIA_ROOT, self.get_directory_name()))
		if not path.startswith(topdir) or path == topdir:
			return
		# Odstránenie prázdneho adresára
		try:
			os.rmdir(path)
		except OSError:
			return
		updir = os.path.join(*os.path.split(path)[:-1])
		if updir.startswith(topdir) and updir != topdir:
			self.__clean_dir(updir)

	def _delete_image(self, instance, **kwargs):
		"""
		Vymazanie obrázka a náhľadov pri odstránení inštancie.
		"""
		field = getattr(instance, self.name)
		if not field:
			return
		path = field.storage.path(field.path)
		self.__perform_remove_file(path)
		self.__clean_dir(os.path.dirname(path))

	def _add_old_instance(self, instance, **kwargs):
		"""
		Zaznamenanie hodnoty starej inštancie
		"""
		if instance.pk:
			setattr(instance, self.name + '_old', getattr(instance, self.name))
		else:
			setattr(instance, self.name + '_old', None)

	@staticmethod
	def get_thumbnail_filename(filename, thumbnail_label):
		"""
		Vráti názov súboru pre zmenšený obrázok.
		"""
		dirname = os.path.dirname(filename)
		splitted_filename = list(os.path.splitext(os.path.basename(filename)))
		splitted_filename.insert(1, u'_' + thumbnail_label)
		return os.path.join(dirname, u''.join(splitted_filename))

	def _add_thumbnails(self, cls, name):
		thumbnail = self.thumbnail or {}

		for label, size in thumbnail.iteritems():
			def wrap(label, size):
				def get_thumbnail(self):
					field = getattr(self, name)
					storage = field.storage
					filename = str(field)
					# Preskakovanie prázdneho poľa
					if not filename:
						return
					# Kontrola zdrojového súboru
					if not os.path.exists(storage.path(filename)):
						return
					thumbnail_file = AutoImageFieldMixin.get_thumbnail_filename(filename, label)
					return ThumbnailField(field, thumbnail_file, size)
				return get_thumbnail
			setattr(cls, name + u'_' + label, property(wrap(label, size)))


class AutoImageField(AutoImageFieldMixin, ImageField):
	def __init__(self, verbose_name=None, size=None, thumbnail=None, *args, **kwargs):
		self.size = size
		self.thumbnail = thumbnail or {}
		super(AutoImageField, self).__init__(verbose_name, *args, **kwargs)

	def contribute_to_class(self, cls, name):
		super(AutoImageField, self).contribute_to_class(cls, name)
		signals.post_save.connect(self._rename_image, sender=cls)
		signals.post_init.connect(self._add_old_instance, sender=cls)
		signals.post_delete.connect(self._delete_image, sender=cls)
		self._add_thumbnails(cls, name)
