# -*- coding: utf-8 -*-
from django import template
from django.contrib.contenttypes.models import ContentType

from hitcount.models import HitCount
from shakal.utils import iterify


register = template.Library()


@register.simple_tag(takes_context = True)
def add_hitcount(context, model):
	model = iterify(model)
	content_type = None
	id_list = []
	for obj in model:
		id_list.append(obj.pk)
		if content_type is None:
			content_type = ContentType.objects.get_for_model(type(obj))
	if not content_type:
		return ''
	hitcounts = HitCount.objects.filter(content_type = content_type, object_id__in = id_list).values('object_id', 'hits')
	hitcounts = dict([(h['object_id'], h['hits']) for h in hitcounts])
	for obj in model:
		obj.display_count = hitcounts.get(obj.pk, 0)
	return ''
