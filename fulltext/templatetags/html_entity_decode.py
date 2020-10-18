# -*- coding: utf-8 -*-
import re
from builtins import chr as chr_
from html.entities import entitydefs

from django import template
from django.utils.encoding import force_str
from django_jinja import library


register = template.Library()

pattern = re.compile(r'&(\w+?);')
dec_pattern = re.compile(r'&\#(\d+?);')


def html_entity_decode_char(m, defs=None):
	defs = defs or entitydefs
	try:
		return force_str(defs[m.group(1)], errors='replace')
	except KeyError:
		return m.group(0)

def xml_entity_decode_char(m):
	try:
		return chr_(int(m.group(1)))
	except (UnicodeError, ValueError):
		return m


@library.filter
@register.filter
def html_entity_decode(string):
	without_entity = pattern.sub(html_entity_decode_char, string)
	text = dec_pattern.sub(xml_entity_decode_char, without_entity)
	text = ' '.join(w[:100] for w in text.split())
	return text
