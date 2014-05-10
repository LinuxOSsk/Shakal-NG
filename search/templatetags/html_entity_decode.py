# -*- coding: utf-8 -*-
import re

import htmlentitydefs
from django import template
from django_jinja import library


register = template.Library()
lib = library.Library()

pattern = re.compile(r'&(\w+?);')
dec_pattern = re.compile(r'&\#(\d+?);')


def html_entity_decode_char(m, defs=None):
	defs = defs or htmlentitydefs.entitydefs
	try:
		return unicode(defs[m.group(1)], errors='replace')
	except KeyError:
		return m.group(0)

def xml_entity_decode_char(m):
	try:
		return unichr(int(m.group(1)))
	except (UnicodeError, ValueError):
		return m


@lib.filter
@register.filter
def html_entity_decode(string):
	without_entity = pattern.sub(html_entity_decode_char, string)
	return dec_pattern.sub(xml_entity_decode_char, without_entity)
