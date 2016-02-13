# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def related_documents(instance, queryset, ordering):
	reverse_ordering = [field[1:] if field[0] == '-' else '-' + field for field in ordering]
	order_asc = queryset.order_by(*ordering)
	order_desc = queryset.order_by(*reverse_ordering)
	next_documents = order_asc
	prev_documents = order_desc
	for field in ordering:
		desc = field[0] == '-'
		if desc:
			field = field[1:]
		next_documents = next_documents.filter(**{
			field + '__' + ('lt' if desc else 'gt'): getattr(instance, field)
		})
		prev_documents = prev_documents.filter(**{
			field + '__' + ('gt' if desc else 'lt'): getattr(instance, field)
		})
	document_relations = {
		'current': instance,
		'next': next_documents.first(),
		'prev': prev_documents.first(),
		'first': order_asc.first(),
		'last': order_desc.first(),
		'prev_query': prev_documents,
		'next_query': next_documents,
	}
	return document_relations
