# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.validators import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import Geoposition
from .forms import GeopositionField as GeopositionFormField


class GeopositionField(models.Field):
	description = _("A geoposition (latitude and longitude)")
	default_error_messages = {
		'invalid': _("Enter a valid geoposition.")
	}

	def __init__(self, *args, **kwargs):
		kwargs['max_length'] = 100
		super(GeopositionField, self).__init__(*args, **kwargs)

	def get_internal_type(self):
		return 'CharField'

	def from_db_value(self, value, *args, **kwargs):
		if not value:
			return None
		if isinstance(value, Geoposition):
			return value
		if isinstance(value, list):
			return Geoposition(value[0], value[1])

		try:
			latitude, longitude = value.split(",")
			return Geoposition(latitude, longitude)
		except Exception: #pylint: disable=broad-except
			raise ValidationError(self.error_messages['invalid'], code='invalid')

	def get_prep_value(self, value):
		if not value:
			return ''
		else:
			return str(value)

	def formfield(self, **kwargs):
		defaults = {
			'form_class': GeopositionFormField
		}
		defaults.update(kwargs)
		return super(GeopositionField, self).formfield(**defaults)
