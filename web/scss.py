# -*- coding: utf-8 -*-
import math
from copy import deepcopy

import xml.etree.ElementTree as ET
import sass
from django.contrib.staticfiles import finders
from django.template.defaultfilters import urlencode
import logging


logger = logging.getLogger(__name__)


svg_cache = {
}


def load_svg_doc(filename, copy=True):
	#if filename in svg_cache:
	#	doc = svg_cache[filename]
	#else:
	static_filename = finders.find(filename)
	if static_filename is None:
		raise RuntimeError(f"File `{filename}` not found")
	svg_cache[filename] = ET.parse(static_filename)
	doc = svg_cache[filename]
	if copy:
		doc = deepcopy(doc)
	return doc


def scss_load_svg(filename, stylesheet):
	try:
		doc = load_svg_doc(filename, copy=bool(stylesheet))
		if stylesheet:
			style_element = ET.Element("{http://www.w3.org/2000/svg}style")
			style_element.text = stylesheet
			doc.getroot().insert(0, style_element)
		return 'data:image/svg+xml,' + urlencode(ET.tostring(doc.getroot(), encoding='utf-8', xml_declaration=True).decode('utf-8'), '')
	except Exception as e:
		logger.exception("Load svg failed")
		return str(e)

def scss_info_svg(filename):
	try:
		doc = load_svg_doc(filename, copy=False)
		view_box = doc.getroot().attrib['viewBox']
		view_box = [float(val) for val in view_box.strip().split()]
		w = math.ceil(view_box[2])
		h = math.ceil(view_box[3])

		return {'w': sass.SassNumber(w, 'px'), 'h': sass.SassNumber(h, 'px')}
	except Exception:
		logger.exception("Load svg failed")
		return {'w': sass.SassNumber(0, 'px'), 'h': sass.SassNumber(0, 'px')}
