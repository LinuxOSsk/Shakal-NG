# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal


class Geoposition(object):
	def __init__(self, latitude, longitude):
		self.latitude = Decimal(str(latitude))
		self.longitude = Decimal(str(longitude))

	def __str__(self):
		return "%s,%s" % (str(self.latitude), str(self.longitude))

	def __eq__(self, other):
		return isinstance(other, self.__class__) and self.latitude == other.latitude and self.longitude == other.longitude

	def __ne__(self, other):
		return not isinstance(other, self.__class__) or self.latitude != other.latitude or self.longitude != other.longitude
