# -*- coding: utf-8 -*-
from rich_editor.parser import HtmlParser, ONELINE_TAGS


def get_parser(editor_type):
	if editor_type == 'signature':
		supported_tags = ONELINE_TAGS
		supported_tags['a'].req_attributes['rel'] = 'nofollow'
		return HtmlParser(supported_tags = supported_tags)
	else:
		return HtmlParser()
