# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django_jinja import library

from common_utils import iterify
from hitcount.models import HitCount


@library.global_function
def add_hitcount(model):
	model = iterify(model)
	content_type = None
	if len(model) == 0:
		return ''
	id_list = [o.pk for o in model]
	content_type = ContentType.objects.get_for_model(model[0].__class__)
	hitcounts = HitCount \
		.objects \
		.filter(content_type = content_type, object_id__in = id_list) \
		.values_list('object_id', 'hits')
	hitcounts = dict(hitcounts)
	for obj in model:
		obj.display_count = hitcounts.get(obj.pk, 0)
	return ''
