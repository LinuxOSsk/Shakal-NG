# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType

from common_utils import iterify


def get_lookups(models):
	lookups = {}
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
			lookups.setdefault(content_type, [])
			lookups[content_type] += id_list
			content_types.append(content_type)
		else:
			content_types.append(None)

	return lookups, content_types
