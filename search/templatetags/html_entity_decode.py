# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from builtins import chr as chr_
from django import template
from django.utils.encoding import force_text
from django_jinja import library
from html.entities import entitydefs


register = template.Library()

pattern = re.compile(r'&(\w+?);')
dec_pattern = re.compile(r'&\#(\d+?);')


def html_entity_decode_char(m, defs=None):
	defs = defs or entitydefs
	try:
		return force_text(defs[m.group(1)], errors='replace')
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
	return dec_pattern.sub(xml_entity_decode_char, without_entity)
