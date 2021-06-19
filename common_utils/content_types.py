# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType

from common_utils import iterify, get_default_manager


def get_lookups(models):
	lookups = {}
	content_types = []

	for model in models:
		model = iterify(model)

		id_list = []
		last_object = None
		object_cls = None
		for o in model:
			if o is None:
				continue
			id_list.append(o.pk)
			last_object = o
			if object_cls is None:
				object_cls = o.__class__
			elif object_cls is not o.__class__:
				raise ValueError('Heterogenous list')

		if last_object is not None:
			content_type = ContentType.objects.get_for_model(last_object.__class__)
			lookups.setdefault(content_type, [])
			lookups[content_type] += id_list
			content_types.append(content_type)
		else:
			content_types.append(None)

	return lookups, content_types


def resolve_content_objects(content_object_list):
	object_list_by_content = {}
	for obj in content_object_list:
		object_list_by_content.setdefault(obj[0], [])
		object_list_by_content[obj[0]].append(obj[1])
	content_types = {obj.id: obj for obj in ContentType.objects.filter(pk__in=object_list_by_content.keys())}

	for content_type, content_object_ids in object_list_by_content.items():
		object_list_by_content[content_type] = (get_default_manager(content_types[content_type].model_class())
			.filter(pk__in=content_object_ids))

	objects_idx = {}
	for content_type, content_objects in object_list_by_content.items():
		for content_object in content_objects:
			objects_idx[(content_type, content_object.pk)] = content_object

	object_list = [objects_idx.get((o[0], int(o[1]))) for o in content_object_list]
	return object_list
