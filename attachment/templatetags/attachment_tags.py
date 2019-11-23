# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django_jinja import library

from ..models import AttachmentImage


@library.global_function
def attached_images(obj, min_size=None):
	ctype = ContentType.objects.get_for_model(obj.__class__)
	images = AttachmentImage.objects.filter(content_type=ctype, object_id=obj.pk)
	if min_size is not None:
		images = images.filter(width__gte=min_size[0], height__gte=min_size[1])
	return list(images)
