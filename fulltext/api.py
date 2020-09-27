# -*- coding: utf-8 -*-
import re

from django.contrib.contenttypes.models import ContentType
from django.db import connections
from django.db.models import Exists, OuterRef

from .models import SearchIndex
from .utils import bulk_update, search_simple, search_postgres, iterate_qs


HIGHLIGHT_REGEX = re.compile(re.escape(SearchIndex.HIGHLIGHT_START) + '(.*?)' + re.escape(SearchIndex.HIGHLIGHT_STOP), re.MULTILINE | re.DOTALL)
HIGHLIGHT_REGEX_START = re.compile(re.escape(SearchIndex.HIGHLIGHT_START), re.MULTILINE | re.DOTALL)
HIGHLIGHT_REGEX_STOP = re.compile(re.escape(SearchIndex.HIGHLIGHT_STOP), re.MULTILINE | re.DOTALL)
BATCH_SIZE = 1000
ELLIPSIS = '…'


def update_search_index(index, progress=None):
	if progress is None:
		progress = lambda iterable: iterable

	bulk_items = []
	content_type = ContentType.objects.get_for_model(index.get_model())

	queryset = index.get_index_queryset()

	(SearchIndex.objects
		.annotate(obj_exists=Exists(queryset.values('pk').filter(pk=OuterRef('object_id'))))
		.filter(content_type=content_type, obj_exists=False)
		.delete())

	for obj in progress(iterate_qs(queryset, BATCH_SIZE), desc=index.get_model().__name__, total=queryset.values('pk').count()):
		instance = index.get_index(obj)
		instance.content_type = content_type
		instance.object_id = obj.pk
		bulk_items.append(instance)
		if len(bulk_items) >= BATCH_SIZE:
			bulk_update(bulk_items)
			bulk_items = []
	if bulk_items:
		bulk_update(bulk_items)


def search(term, search_document=True, search_comments=True):
	if search_document is None and search_comments is None:
		return SearchIndex.objects.none()
	index = SearchIndex.objects.all()
	connection = connections[index.db]
	if connection.vendor == 'postgresql':
		return search_postgres(term, search_document=search_document, search_comments=search_comments)
	else:
		return search_simple(term, search_document=search_document, search_comments=search_comments)


def highlight(text, start, end, length=None, ellipsis=None):
	ellipsis = ellipsis or ELLIPSIS
	def repl(match):
		return f'{start}{match.group(1)}{end}'
	if length is not None:
		highlight = HIGHLIGHT_REGEX.search(text)
		if highlight is None:
			space = text.find(' ', length)
			if space == -1:
				text = text[:length]
			else:
				text = text[:space]
		else:
			span = highlight.span()
			span = [span[0], span[1]]
			current_length = span[1] - span[0] - len(SearchIndex.HIGHLIGHT_START) - len(SearchIndex.HIGHLIGHT_STOP)
			expand = length - current_length
			if expand > 0:
				span[0] -= expand // 2
				span[1] += expand // 2
			if span[0] < 0:
				span[1] -= span[0]
				span[0] = 0
			span[0] = text.rfind(' ', 0, span[0]) + 1
			space = text.find(' ', span[1])
			if space != -1:
				span[1] = space
			prefix = ''
			suffix = ''
			if span[0] > 0:
				prefix = ellipsis
			if span[1] < len(text) - 1:
				suffix = ellipsis
			text = prefix + text[span[0]:span[1]] + suffix
	return HIGHLIGHT_REGEX_START.sub('',HIGHLIGHT_REGEX_STOP.sub('', HIGHLIGHT_REGEX.sub(repl, text)))
