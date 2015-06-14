# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django_jinja import library

from common_utils import iterify
from hitcount.models import HitCount


@library.global_function
def add_hitcount(*models):
	hitcounts_lookups = {}
	content_types = []

	for model in models:
		model = iterify(model)

		id_list = []
		last_object = None
		for o in model:
			id_list.append(o.pk)
			last_object = o

		if last_object is not None:
			content_type = ContentType.objects.get_for_model(last_object.__class__)
			hitcounts_lookups.setdefault(content_type, [])
			hitcounts_lookups[content_type] += id_list
			content_types.append(content_type)
		else:
			content_types.append(None)

	if not hitcounts_lookups:
		return ''

	hitcount_q = None

	for content_type, ids in hitcounts_lookups.iteritems():
		q = Q(content_type=content_type, object_id__in=ids)
		hitcount_q = q if hitcount_q is None else hitcount_q | q

	hitcounts = HitCount.objects.all().\
		filter(q).\
		values_list('object_id', 'content_type_id', 'hits')
	hitcounts_dict = {h[:2]: h[2] for h in hitcounts}

	for model, content_type in zip(models, content_types):
		for obj in model:
			obj.display_count = hitcounts_dict.get((obj.pk, content_type.pk))

	return ''
