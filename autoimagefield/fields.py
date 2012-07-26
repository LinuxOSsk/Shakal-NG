# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models import signals
from django.db.models.fields.files import ImageField
import os
import shutil


class ThumbnailField(object):
	"""
	Inštancia sa pužíva na prístup k náhľadom
	"""
	def __init__(self, field, filename = None, size = None):
		self.filename = filename
		self.field = field
		self.thumbnail_size = size

	def _initialize_file(self):
		dest_filename = self.field.storage.path(self.filename)
		if os.path.exists(dest_filename):
			return

		source_filename = self.field.storage.path(str(self.field))
		if not os.path.exists(source_filename):
			return

		# Kópia a resize obrázku
		shutil.copy(source_filename, dest_filename)
		AutoImageField.resize_image(dest_filename, self.thumbnail_size)

	def _get_path(self):
		#self._initialize_file()
		return self.field.storage.path(self.filename)
	path = property(_get_path)

	def _get_url(self):
		self._initialize_file()
		return self.field.storage.url(self.filename)
	url = property(_get_url)

	def _get_size(self):
		#self._initialize_file()
		return self.field.storage.size(self.filename)
	size = property(_get_size)


class AutoImageField(ImageField):
	WIDTH, HEIGHT = 0, 1

	def __init__(self, size = None, thumbnail = None, *args, **kwargs):
		self.size = size
		self.thumbnail = {}
		if thumbnail:
			self.thumbnail = thumbnail
		super(AutoImageField, self).__init__(*args, **kwargs)

	@staticmethod
	def resize_image(filename, size):
		import Image
		img = Image.open(filename)
		if img.size[AutoImageField.WIDTH] > size[AutoImageField.WIDTH] or img.size[AutoImageField.HEIGHT] > size[AutoImageField.HEIGHT]:
			img.thumbnail((size[AutoImageField.WIDTH], size[AutoImageField.HEIGHT]), Image.ANTIALIAS)
		try:
			img.save(filename, optimize = 1)
		except IOError:
			img.save(filename)

	def get_object_pk(self, instance):
		return instance.pk

	def generate_filename(self, instance, filename):
		if self.get_object_pk(instance):
			return os.path.join(self.get_directory_name(), "{0:02x}".format(self.get_object_pk(instance) % 256), str(self.get_object_pk(instance)), self.get_filename(filename))
		else:
			return super(AutoImageField, self).generate_filename(instance, filename)

	def __rename_image(self, instance, **kwargs):
		field = getattr(instance, self.name)
		new_file = None
		# Pôvodná adresa
		try:
			src = os.path.abspath(field.path)
			ext = os.path.splitext(src)[1].lower().replace('jpg', 'jpeg')
			new_file = self.generate_filename(instance, "{0}_{1}{2}".format(self.name, instance.pk, ext))
			dest = os.path.abspath(os.path.join(settings.MEDIA_ROOT, new_file))
		except ValueError:
			src = None

		if src and src != dest and os.path.exists(src):
			if not os.path.exists(os.path.dirname(dest)):
				os.makedirs(os.path.dirname(dest))
			# Ak má pole atribút force_copy namiesto presunu sa kopíruje
			if getattr(instance, 'force_copy', False):
				shutil.copy(src, dest)
			else:
				os.rename(src, dest)

			# Presun / kópia náhľadov
			for label in self.thumbnail:
				old_tmb = self.__get_thumbnail_filename(src, label)
				new_tmb = self.__get_thumbnail_filename(dest, label)
				if os.path.exists(old_tmb):
					if getattr(instance, 'force_copy', False):
						shutil.copy(old_tmb, new_tmb)
					else:
						os.rename(old_tmb, new_tmb)
			setattr(instance, self.name, new_file)
			instance.save()

		# Ak je definovaná veľkosť škálujeme obrázok
		if src:
			if self.size:
				self.resize_image(dest, self.size)
			self.__add_thumbnails(instance, force = True, **kwargs)

		# Odstránenie starého súboru pri nahradení novým s inou príponou
		old = getattr(instance, self.name + '_old', None)
		if old and old != new_file and os.path.exists(field.storage.path(old)):
			oldfile = field.storage.path(old)
			os.remove(oldfile)
			for label in self.thumbnail:
				tmb_filename = self.__get_thumbnail_filename(oldfile, label)
				if os.path.exists(tmb_filename):
					os.remove(tmb_filename)
			instance.old = new_file
		self.__clean_dir(os.path.dirname(src))

	def __clean_dir(self, path):
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

	def __delete_image(self, instance, **kwargs):
		"""
		Vymazanie obrázka a náhľadov pri odstránení inštancie.
		"""
		field = getattr(instance, self.name)
		path = os.path.abspath(field.path)
		if os.path.exists(path):
			os.remove(path)
			for label in self.thumbnail:
				tmb_filename = self.__get_thumbnail_filename(path, label)
				if os.path.exists(tmb_filename):
					os.remove(tmb_filename)
		self.__clean_dir(os.path.dirname(path))

	def __add_old_instance(self, instance, **kwargs):
		"""
		Zaznamenanie hodnoty starej inštancie
		"""
		if instance.pk:
			setattr(instance, self.name + '_old', getattr(instance, self.name))
		else:
			setattr(instance, self.name + '_old', None)

	def __get_thumbnail_filename(self, filename, thumbnail_label):
		"""
		Vráti názov súboru pre zmenšený obrázok.
		"""
		dirname = os.path.dirname(filename)
		splitted_filename = list(os.path.splitext(os.path.basename(filename)))
		splitted_filename.insert(1, u'_' + thumbnail_label)
		return os.path.join(dirname, u''.join(splitted_filename))

	def __add_thumbnails(self, instance, force = False, **kwargs):
		"""
		Pridanie polí pre náhľady
		"""
		if not self.thumbnail:
			return

		# Nastavenie prázdnych polí pre náhľady
		field = getattr(instance, self.name)
		storage = field.storage
		filename = str(field)
		# Preskakovanie prázdneho poľa
		if not filename:
			return
		# Kontrola zdrojového súboru
		try:
			if not os.path.exists(storage.path(filename)):
				return
		except:
			return
		# Nastavenie jednotlivých náhľadov
		for label, size in self.thumbnail.iteritems():
			thumbnail_file = self.__get_thumbnail_filename(filename, label)
			setattr(field, u'thumbnail_' + label, ThumbnailField(field, thumbnail_file, size))

	def contribute_to_class(self, cls, name):
		signals.post_save.connect(self.__rename_image, sender = cls)
		signals.post_init.connect(self.__add_old_instance, sender = cls)
		signals.post_init.connect(self.__add_thumbnails, sender = cls)
		signals.post_delete.connect(self.__delete_image, sender = cls)
		super(AutoImageField, self).contribute_to_class(cls, name)
