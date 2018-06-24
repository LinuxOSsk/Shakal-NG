# -*- coding: utf-8 -*-
# pylint: disable=abstract-method
from __future__ import unicode_literals

import re

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

	def parse_query(self, query_string):
		try:
			return super().parse_query(query_string)
		except xapian.QueryParserError:
			return xapian.Query()

	@staticmethod
	def _do_highlight(content, query, tag='em'):
		for term in query:
			term = term.decode('utf-8')
			for match in re.findall('[^A-Z]+', term):  # Ignore field identifiers
				match_re = re.compile(re.escape(match), re.I)
				content = match_re.sub('<%s>%s</%s>' % (tag, term, tag), content)

		return content


class XapianEngine(BaseEngine):
	backend = XapianSearchBackend
	query = XapianSearchQuery
