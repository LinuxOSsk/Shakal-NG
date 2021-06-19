# -*- coding: utf-8 -*-
from django.db.models import Q
from django_jinja import library

from ..cache import cache
from ..models import HitCount
from common_utils.content_types import get_lookups


@library.global_function
def add_hitcount(*models):
	hitcounts_lookups, content_types = get_lookups(models)

	hitcounts_lookups = {content_type: [i for i in id_list if (i, content_type.pk) not in cache.cache] for content_type, id_list in hitcounts_lookups.items()}
	hitcounts_lookups = {content_type: id_list for content_type, id_list in hitcounts_lookups.items() if id_list}

	for model, content_type in zip(models, content_types):
		for obj in model:
			obj.display_count = cache.cache.get((obj.pk, content_type.pk), None)

	if not hitcounts_lookups:
		return ''

	hitcount_q = Q()
	for content_type, ids in hitcounts_lookups.items():
		hitcount_q = hitcount_q | Q(content_type=content_type, object_id__in=ids)

	hitcounts = HitCount.objects.all().\
		filter(hitcount_q).\
		values_list('object_id', 'content_type_id', 'hits')
	hitcounts_dict = {h[:2]: h[2] for h in hitcounts}

	for model, content_type in zip(models, content_types):
		for obj in model:
			key = (obj.pk, content_type.pk)
			count = cache.cache.get(key, hitcounts_dict.get(key))
			obj.display_count = count
			cache.cache[key] = count

	cache.save()

	return ''
