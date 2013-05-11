# -*- coding: utf-8 -*-
from rich_editor.parser import HtmlParser, HtmlTag, HrefValidator, NofollowValidator, ONELINE_TAGS, DEFAULT_TAGS
from copy import deepcopy


def get_parser(editor_type):
	if editor_type == 'signature':
		supported_tags = deepcopy(ONELINE_TAGS)
		supported_tags['a'].req_attributes['rel'] = 'nofollow'
		supported_tags['a'].attribute_validators = {'rel': [NofollowValidator()]}
		return HtmlParser(supported_tags = supported_tags)
	elif editor_type == 'profile':
		supported_tags = deepcopy(DEFAULT_TAGS)
		supported_tags['img'] = HtmlTag('img', opt = [''], req_attributes = {'src': ''}, empty = True, attribute_validators = {'src': [HrefValidator()]})
		supported_tags[''] = HtmlTag('', opt = ['', 'a', 'b', 'u', 'br', 'p', 'i', 'em', 'code', 'strong', 'pre', 'blockquote', 'ol', 'ul', 'span', 'cite', 'img'])
		return HtmlParser(supported_tags = supported_tags)
	else:
		return HtmlParser()
