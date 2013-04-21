# -*- coding: utf-8 -*-

from django import template
from django.template.defaultfilters import slugify
from django_tools.middlewares.ThreadLocal import get_current_request


def process_template_args(rawparams, context = None):
	args = []
	for param in rawparams:
		pos = param.find('=')
		if (pos > 0):
			break
		if context is not None:
			param = template.resolve_variable(param, context)
		args.append(param)
	return args


def process_template_kwargs(rawparams, context = None):
	kwargs = {}
	for param in rawparams:
		paramname = param
		paramvalue = ''
		pos = param.find('=')
		if (pos <= 0):
			continue
		paramname = param[:pos]
		paramvalue = param[pos + 1:]
		if context is not None:
			paramvalue = template.resolve_variable(paramvalue, context)
		kwargs[paramname] = paramvalue
	return kwargs


def unique_slugify(item, title_field, slug_field = 'slug', reserve_chars = 5):
	if not getattr(item, slug_field):
		slug_field_object = item._meta.get_field(slug_field)
		slug_length = slug_field_object.max_length
		slug = slugify(getattr(item, title_field))[:slug_length - reserve_chars]

		queryset = item.__class__._default_manager.all()
		if item.pk:
			queryset = queryset.exclude(pk = item.pk)

		slug_field_query = slug_field + '__startswith'
		all_slugs = set(queryset.filter(**{slug_field_query: slug}).values_list(slug_field, flat = True))
		max_val = 10**(reserve_chars - 1) - 1
		setattr(item, slug_field, create_unique_slug(slug, all_slugs, max_val))


def create_unique_slug(slug, all_slugs, max_val):
	if not slug in all_slugs:
		return slug
	else:
		for suffix in xrange(2, max_val):
			new_slug = slug + '-' + str(suffix)
			if not new_slug in all_slugs:
				return new_slug
	return slug


def iterify(items):
	try:
		iter(items)
		return items
	except:
		return [items]


def build_absolute_uri(path):
	request = get_current_request()
	if request:
		return request.build_absolute_uri(path)
	else:
		from django.conf import settings
		from django.contrib.sites.models import Site
		return 'http://' + Site.objects.get(pk = settings.SITE_ID) + path
