# -*- coding: utf-8 -*-
# pylint: disable=abstract-method
from __future__ import unicode_literals

import xapian
from haystack.backends import BaseEngine
from xapian_backend import XapianSearchBackend as CoreXapianSearchBackend, XapianSearchQuery


class XapianSearchBackend(CoreXapianSearchBackend):
	def _database(self, *args, **kwargs):
		database = super(XapianSearchBackend, self)._database(*args, **kwargs)
		if not hasattr(database, 'replace_document'):
			return database
		old_replace_document = database.replace_document

		def replace_document(document_id, document):
			try:
				return old_replace_document(document_id, document)
			except xapian.InvalidArgumentError:
				pass

		database.replace_document = replace_document
		return database


class XapianEngine(BaseEngine):
	backend = XapianSearchBackend
	query = XapianSearchQuery
