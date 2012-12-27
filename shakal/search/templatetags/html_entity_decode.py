# -*- coding: utf-8 -*-

import htmlentitydefs
import re
from django import template

register = template.Library()

pattern = re.compile("&(\w+?);")

def html_entity_decode_char(m, defs=htmlentitydefs.entitydefs):
	try:
		return defs[m.group(1)]
	except KeyError:
		return m.group(0)

@register.filter
def html_entity_decode(string):
	return pattern.sub(html_entity_decode_char, string)
