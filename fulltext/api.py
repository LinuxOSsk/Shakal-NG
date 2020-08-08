# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.db import connections
from django.db.models import Exists, OuterRef

from .models import SearchIndex
from .utils import bulk_update, search_simple, search_postgres


BATCH_SIZE = 1000


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

	for obj in progress(queryset, desc=index.get_model().__name__):
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
	index = SearchIndex.objects.all()
	connection = connections[index.db]
	if connection.vendor == 'postgresql':
		return search_postgres(term, search_document=search_document, search_comments=search_comments)
	else:
		return search_simple(term, search_document=search_document, search_comments=search_comments)
