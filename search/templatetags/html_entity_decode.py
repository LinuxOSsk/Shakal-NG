# -*- coding: utf-8 -*-
import re

import htmlentitydefs
from django import template
from django_jinja import library


register = template.Library()
lib = library.Library()

pattern = re.compile("&(\w+?);")
dec_pattern = re.compile("&\\#(\d+?);")

def html_entity_decode_char(m, defs=htmlentitydefs.entitydefs):
	try:
		return defs[m.group(1)]
	except KeyError:
		return m.group(0)

def xml_entity_decode_char(m):
	try:
		return unichr(int(m.group(1)))
	except:
		return m

@lib.filter
@register.filter
def html_entity_decode(string):
	return dec_pattern.sub(xml_entity_decode_char, pattern.sub(html_entity_decode_char, string))
