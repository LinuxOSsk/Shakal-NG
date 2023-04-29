# -*- coding: utf-8 -*-
import logging
from copy import deepcopy
from typing import Union, Callable, Tuple

import lxml.html
from lxml import etree


logger = logging.getLogger(__name__)


def unwrap_tag(content) -> Tuple[str, str, str]:
	"""
	Unwraps tag and returns content, start of tag and end of tag
	"""
	tag_begin = content[:content.find('>')+1]
	tag_end = content[content.rfind('<'):]
	return content[content.find('>')+1:content.rfind('<')], tag_begin, tag_end


def replace_element(element: etree.ElementBase, content: Union[etree.ElementBase, Callable, str]):
	# if it's callable, call it
	if callable(content):
		e = deepcopy(element)
		e.tail = ''
		content = content(e)
	# if it's element, convert it to string
	if not isinstance(content, str):
		content = etree.tostring(content, encoding='utf-8').decode('utf-8')

	fragments = lxml.html.fragments_fromstring(content)
	previous = element.getprevious()
	parent = element.getparent()

	for fragment in fragments:
		if isinstance(fragment, str):
			if previous is None:
				parent.text = (parent.text or '') + fragment
			else:
				parent.tail = (parent.tail or '') + fragment
		else:
			element.addprevious(fragment)
	element.drop_tree()


def highlight_code(element, lang):
	content = etree.tostring(element, encoding='utf-8', method='html').decode('utf-8')
	content, tag_begin, tag_end = unwrap_tag(content)
	try:
		code = format_code(content, lang)
		return f'{tag_begin}{code}{tag_end}'
	except Exception:
		logger.exception("Failed to highlight code")
		return element
