# -*- coding: utf-8 -*-
from django.db.models import Q

from .models import SearchIndex


def bulk_update(items):
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
		SearchIndex.objects.bulk_update(to_update, fields=['created', 'updated', 'author', 'authors_name', 'title', 'document', 'comments', 'language_code'])
	SearchIndex.objects.filter(content_type_id=items[0].content_type_id, object_id__in=pks).update_search_index()


def search_simple(term, search_document=True, search_comments=True):
	q = Q()
	term = term.split()
	if search_document:
		document_q = Q()
		for t in term:
			document_q &= Q(document__icontains=t)
		q |= document_q
	if search_comments:
		comments_q = Q()
		for t in term:
			comments_q &= Q(comments__icontains=t)
		q |= comments_q
	return SearchIndex.objects.filter(q)
