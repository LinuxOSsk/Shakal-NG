# -*- coding: utf-8 -*-
from rich_editor.parser import HtmlParser, HtmlTag, HrefValidator, NofollowValidator, ONELINE_TAGS, DEFAULT_TAGS
from copy import deepcopy, copy


def get_parser(editor_type):
	if editor_type == 'signature':
		supported_tags = copy(ONELINE_TAGS)
		supported_tags['a'] = deepcopy(supported_tags['a'])
		supported_tags['a'].req_attributes['rel'] = 'nofollow'
		supported_tags['a'].attribute_validators = {'rel': [NofollowValidator()]}
		parser = HtmlParser(supported_tags = supported_tags)
		parser.auto_paragraphs = False
		return parser
	elif editor_type == 'profile' or editor_type == 'blog':
		supported_tags = copy(DEFAULT_TAGS)
		supported_tags['img'] = HtmlTag('img', opt = ['title'], req_attributes = {'src': '', 'alt': ''}, empty = True, attribute_validators = {'src': [HrefValidator()]})
		supported_tags[''] = deepcopy(supported_tags[''])
		supported_tags[''].opt.add('img')
		return HtmlParser(supported_tags = supported_tags)
	else:
		return HtmlParser()
