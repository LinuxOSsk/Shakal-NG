# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import importlib
from django.utils.safestring import mark_safe
from django_jinja import library


@library.global_function
def highlight(text_block, query, **kwargs):
	try:
		path_bits = getattr(settings, 'HAYSTACK_CUSTOM_HIGHLIGHTER', 'haystack.utils.Highlighter').split('.')
		highlighter_path, highlighter_classname = '.'.join(path_bits[:-1]), path_bits[-1]
		highlighter_module = importlib.import_module(highlighter_path)
		highlighter_class = getattr(highlighter_module, highlighter_classname)
	except (ImportError, AttributeError) as e:
		raise ImproperlyConfigured("The highlighter '%s' could not be imported: %s" % (settings.HAYSTACK_CUSTOM_HIGHLIGHTER, e))

	highlighter = highlighter_class(query, **kwargs)
	highlighted_text = highlighter.highlight(text_block)
	return mark_safe(highlighted_text)
