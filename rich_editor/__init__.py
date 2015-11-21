# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from copy import deepcopy, copy

from rich_editor.parser import HtmlParser, HtmlTag, HrefValidator, NofollowValidator, ONELINE_TAGS, DEFAULT_TAGS, FULL_TAGS, RawParser


def get_parser(parser, fmt='html'):
	if fmt == 'raw':
		return RawParser()
	else:
		if parser == 'signature':
			supported_tags = copy(ONELINE_TAGS)
			supported_tags['a'] = deepcopy(supported_tags['a'])
			supported_tags['a'].req_attributes['rel'] = 'nofollow'
			supported_tags['a'].attribute_validators = {'rel': [NofollowValidator()]}
			parser_instance = HtmlParser(supported_tags = supported_tags)
			parser_instance.auto_paragraphs = False
			return parser_instance
		elif parser == 'profile':
			supported_tags = copy(DEFAULT_TAGS)
			supported_tags['img'] = HtmlTag('img', opt_attributes=['title'], req_attributes={'src': '', 'alt': ''}, empty=True, attribute_validators = {'src': [HrefValidator()]})
			supported_tags[''] = deepcopy(supported_tags[''])
			supported_tags[''].opt.add('img')
			return HtmlParser(supported_tags = supported_tags)
		elif parser == 'blog':
			supported_tags = copy(FULL_TAGS)
			supported_tags['a'] = deepcopy(supported_tags['a'])
			supported_tags['a'].req_attributes['rel'] = 'nofollow'
			supported_tags['a'].attribute_validators = {'rel': [NofollowValidator()]}
			parser_instance = HtmlParser(supported_tags=supported_tags)
			parser_instance.auto_paragraphs = False
			return parser_instance
		else:
			return HtmlParser()
