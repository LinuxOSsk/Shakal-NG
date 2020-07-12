# -*- coding: utf-8 -*-
from django.utils.functional import cached_property


class FulltextRegister(object):
	def __init__(self):
		self.__registered = []

	def __iter__(self):
		return iter(self.__registered)

	def register(self, fulltext):
		fulltext.register = self
		self.__registered.append(fulltext)

	@cached_property
	def index_class(self):
		from .models import SearchIndex
		return SearchIndex

	@cached_property
	def updated_field(self):
		return self.index_class.get_updated_field()


register = FulltextRegister()
