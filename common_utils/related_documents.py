# -*- coding: utf-8 -*-
def related_documents(instance, queryset, ordering, select_range=0):
	reverse_ordering = [field[1:] if field[0] == '-' else '-' + field for field in ordering]
	order_asc = queryset.order_by(*ordering)
	order_desc = queryset.order_by(*reverse_ordering)
	next_documents = order_asc
	prev_documents = order_desc
	for field in ordering:
		desc = field[0] == '-'
		if desc:
			field = field[1:]
		field_value = instance
		for field_part in field.split('__'):
			field_value = getattr(field_value, field_part)
		next_documents = next_documents.filter(**{
			field + '__' + ('lt' if desc else 'gt'): field_value
		})
		prev_documents = prev_documents.filter(**{
			field + '__' + ('gt' if desc else 'lt'): field_value
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
	if select_range:
		document_relations['range'] = list(reversed(prev_documents[:select_range])) + [instance] + list(next_documents[:select_range])
	return document_relations
