# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType

from .models import SearchIndex


BATCH_SIZE = 1000


def update_search_index(index, progress=None):
	if progress is None:
		progress = lambda iterable: iterable

	bulk_items = []
	content_type = ContentType.objects.get_for_model(index.get_model())

	queryset = index.get_index_queryset()

	for obj in progress(queryset, desc=index.get_model().__name__):
		instance = index.get_index(obj)
		instance.content_type = content_type
		instance.object_id = obj.pk
		bulk_items.append(instance)
		if len(bulk_items) >= BATCH_SIZE:
			__bulk_update(bulk_items)
			bulk_items = []
	if bulk_items:
		__bulk_update(bulk_items)


def __bulk_update(items):
	pks = [item.object_id for item in items]
	existing = dict(SearchIndex.objects.filter(content_type_id=items[0].content_type_id, object_id__in=pks).values_list('object_id', 'pk'))
	to_create = []
	to_update = []
	for item in items:
		pk = existing.get(item.object_id)
		if pk is None:
			to_create.append(item)
		else:
			item.pk = pk
			to_update.append(item)
	if to_create:
		SearchIndex.objects.bulk_create(to_create, ignore_conflicts=True)
	if to_update:
		SearchIndex.objects.bulk_update(to_update, fields=['created', 'updated', 'author', 'authors_name', 'title', 'document', 'comments'])
	SearchIndex.objects.filter(content_type_id=items[0].content_type_id, object_id__in=pks).update_search_index()
