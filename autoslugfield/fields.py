# -*- coding: utf-8 -*-
from django.db.models import signals, SlugField
from django.template.defaultfilters import slugify


class AutoSlugField(SlugField):
	def __init__(self, reserve_chars = 5, title_field = None, *args, **kwargs):
		super(AutoSlugField, self).__init__(*args, **kwargs)
		self.reserve_chars = reserve_chars
		self.title_field = title_field

	def contribute_to_class(self, cls, name):
		signals.pre_save.connect(self.unique_slugify, sender = cls)
		super(AutoSlugField, self).contribute_to_class(cls, name)

	def unique_slugify(self, instance, **kwargs):
		slug = getattr(instance, self.name)
		if not slug:
			if self.title_field:
				slug = slugify(getattr(instance, self.title_field))
			else:
				return

		slug_field = instance._meta.get_field(self.name)
		slug_length = slug_field.max_length
		slug = slug[:slug_length - self.reserve_chars]

		queryset = instance.__class__._default_manager.all()
		if instance.pk:
			queryset = queryset.exclude(pk = instance.pk)

		slug_field_query = self.name + '__startswith'
		all_slugs = set(queryset.filter(**{slug_field_query: slug}).values_list(self.name, flat = True))
		max_val = 10 ** (self.reserve_chars - 1) - 1
		setattr(instance, self.name, self.create_unique_slug(slug, all_slugs, max_val))

	@staticmethod
	def create_unique_slug(slug, all_slugs, max_val):
		if not slug in all_slugs:
			return slug
		else:
			for suffix in xrange(2, max_val):
				new_slug = slug + '-' + str(suffix)
				if not new_slug in all_slugs:
					return new_slug
		return slug
