# -*- coding: utf-8 -*-
from rich_editor.parser import HtmlParser, RawParser, TextParser, ONELINE_TAGS_LIST, DEFAULT_TAG_LIST, FULL_TAGS_LIST


def get_parser(parser, fmt='html'):
	if fmt == 'raw':
		return RawParser()
	elif fmt == 'text':
		return TextParser()
	else:
		if parser == 'signature':
			parser_instance = HtmlParser(supported_tags=ONELINE_TAGS_LIST)
			parser_instance.auto_paragraphs = False
			return parser_instance
		elif parser == 'profile':
			parser_instance = HtmlParser(supported_tags=FULL_TAGS_LIST)
			parser_instance.add_nofollow = False
			return parser_instance
		elif parser == 'blog' or parser == 'full':
			parser_instance = HtmlParser(supported_tags=FULL_TAGS_LIST)
			parser_instance.auto_paragraphs = False
			parser_instance.allow_id = 'safe'
			return parser_instance
		elif parser == 'news_short':
			parser_instance = HtmlParser(supported_tags=DEFAULT_TAG_LIST)
			parser_instance.add_nofollow = False
			return parser_instance
		elif parser == 'news_long':
			parser_instance = HtmlParser(supported_tags=FULL_TAGS_LIST)
			parser_instance.add_nofollow = False
			return parser_instance
		else:
			return HtmlParser()
