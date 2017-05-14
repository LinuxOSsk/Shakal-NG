# -*- coding: utf-8 -*-
import copy
import re
from collections import OrderedDict
from io import StringIO

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.template.defaultfilters import linebreaks_filter
from django.utils.html import escape

from common_utils import build_absolute_uri


class HrefValidator(URLValidator):
	def __call__(self, value):
		if len(value) > 0:
			if value[0] == '#':
				if not re.match("[0-9a-zA-Z_-]*", value[1:]):
					raise ValidationError(self.message, code = 'invalid')
				else:
					return
			elif value[0] == '/':
				value = build_absolute_uri(value)
				return super(HrefValidator, self).__call__(value)
		return super(HrefValidator, self).__call__(value)


class NofollowValidator(object):
	def __call__(self, value):
		if value != "nofollow":
			raise ValidationError("Nofollow required", code='invalid')


class TableSpanValidator(object):
	def __call__(self, value):
		try:
			int(value)
		except:
			raise ValidationError("Integer required", code='invalid')


class CodeValidator(object):
	def __call__(self, value):
		if not re.match(r'^code-\w+$', value):
			raise ValidationError('Class not allowed', code='invalid')


class AttributeException(Exception):
	pass


class TagReadException(Exception):
	pass


class ParserError(object):
	def __init__(self):
		self.message = ''


class HtmlTag:
	def __init__(self, name, req = None, opt = None, req_attributes = None, opt_attributes = None, attribute_validators = None, empty = None, trim_empty = False): #pylint: disable=R0913
		self.name = name
		self.req = set(req or [])
		self.opt = set(opt or [])
		self.req_attributes = dict(req_attributes or {})
		self.opt_attributes = set(opt_attributes or [])
		self.attribute_validators = attribute_validators or {}
		self.empty = empty
		self.trim_empty = trim_empty
		self.pos = None

	def get_child_tags(self):
		return self.req.union(self.opt)

ALL_TAGS = ['a', 'abbr', 'acronym', 'address', 'applet', 'area', 'article', 'aside', 'audio', 'b', 'base', 'basefont', 'bdi', 'bdo', 'big', 'blockquote', 'body', 'br', 'button', 'canvas', 'caption', 'center', 'cite', 'code', 'col', 'colgroup', 'command', 'datalist', 'dd', 'del', 'details', 'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'embed', 'fieldset', 'figcaption', 'figure', 'font', 'footer', 'form', 'frame', 'frameset', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'header', 'hgroup', 'hr', 'html', 'i', 'iframe', 'img', 'input', 'ins', 'kbd', 'keygen', 'label', 'legend', 'li', 'link', 'map', 'mark', 'menu', 'meta', 'meter', 'nav', 'noframes', 'noscript', 'object', 'ol', 'optgroup', 'option', 'output', 'p', 'param', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby', 's', 'samp', 'script', 'section', 'select', 'small', 'source', 'span', 'strike', 'strong', 'style', 'sub', 'summary', 'sup', 'table', 'tbody', 'td', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title', 'tr', 'track', 'tt', 'u', 'ul', 'var', 'video', 'wbr']


TEXT_TAGS_LIST = ['', 'b', 'u', 'i', 'em', 'strong', 'a', 'br', 'del', 'ins', 'sub', 'sup']
ONELINE_TAGS_LIST = TEXT_TAGS_LIST[:-1]

DEFAULT_TAGS = dict((t.name, t) for t in [
	HtmlTag('b', opt=TEXT_TAGS_LIST, empty=False),
	HtmlTag('u', opt=TEXT_TAGS_LIST, empty=False),
	HtmlTag('i', opt=TEXT_TAGS_LIST, empty=False),
	HtmlTag('em', opt=TEXT_TAGS_LIST, empty=False),
	HtmlTag('strong', opt=TEXT_TAGS_LIST, empty=False),
	HtmlTag('a', opt=[''], req_attributes={'href': '#'}, empty=False, attribute_validators={'href': [HrefValidator()]}),
	HtmlTag('pre', opt=[''], empty=False, opt_attributes=['class'], attribute_validators={'class': [CodeValidator()]}),
	HtmlTag('p', opt=TEXT_TAGS_LIST + ['span', 'code', 'cite'], empty=False),
	HtmlTag('span', opt=TEXT_TAGS_LIST, empty=False),
	HtmlTag('br', empty=True),
	HtmlTag('del', opt=TEXT_TAGS_LIST, empty=False),
	HtmlTag('ins', opt=TEXT_TAGS_LIST, empty=False),
	HtmlTag('sub', opt=TEXT_TAGS_LIST, empty=False),
	HtmlTag('sup', opt=TEXT_TAGS_LIST, empty=False),
	HtmlTag('code', opt=['', 'b', 'u', 'i', 'em', 'strong'], empty=False),
	HtmlTag('blockquote', opt=TEXT_TAGS_LIST + ['p', 'code', 'pre', 'cite', 'span', 'ol', 'ul'], empty=False),
	HtmlTag('cite', opt=TEXT_TAGS_LIST, empty=False),
	HtmlTag('ol', req=['li'], empty=True),
	HtmlTag('ul', req=['li'], empty=True),
	HtmlTag('li', opt=TEXT_TAGS_LIST + ['ol', 'ul'], empty=None),
	HtmlTag('', opt=['', 'a', 'b', 'u', 'br', 'del', 'ins', 'sub', 'sup', 'p', 'i', 'em', 'code', 'strong', 'pre', 'blockquote', 'ol', 'ul', 'span', 'cite']),
])
ONELINE_TAGS = dict((t.name, t) for t in [
	HtmlTag('b', opt=ONELINE_TAGS_LIST, empty=False),
	HtmlTag('u', opt=ONELINE_TAGS_LIST, empty=False),
	HtmlTag('i', opt=ONELINE_TAGS_LIST, empty=False),
	HtmlTag('em', opt=ONELINE_TAGS_LIST, empty=False),
	HtmlTag('strong', opt=ONELINE_TAGS_LIST, empty=False),
	HtmlTag('a', opt=[''], req_attributes={'href': '#'}, empty=False, attribute_validators = {'href': [HrefValidator()]}),
	HtmlTag('', opt=['', 'a', 'b', 'u', 'i', 'em']),
])
FULL_TEXT_TAGS_LIST = ['', 'b', 'u', 'i', 'em', 'strong', 'a', 'br', 'del', 'ins', 'abbr', 'img', 'sub', 'sup']
FULL_TAGS = dict((t.name, t) for t in [
	HtmlTag('b', opt=FULL_TEXT_TAGS_LIST, empty=False),
	HtmlTag('u', opt=FULL_TEXT_TAGS_LIST, empty=False),
	HtmlTag('i', opt=FULL_TEXT_TAGS_LIST, empty=False),
	HtmlTag('em', opt=FULL_TEXT_TAGS_LIST, empty=False),
	HtmlTag('strong', opt=FULL_TEXT_TAGS_LIST, empty=False),
	HtmlTag('a', opt=[''], req_attributes={'href': '#'}, empty=False, attribute_validators = {'href': [HrefValidator()]}),
	HtmlTag('pre', opt=[''], empty=False, opt_attributes=['class'], attribute_validators={'class': [CodeValidator()]}),
	HtmlTag('p', opt=FULL_TEXT_TAGS_LIST + ['span', 'code', 'cite'], empty=False),
	HtmlTag('span', opt=FULL_TEXT_TAGS_LIST, empty=False),
	HtmlTag('br', empty=True),
	HtmlTag('del', opt=FULL_TEXT_TAGS_LIST, empty=False),
	HtmlTag('ins', opt=FULL_TEXT_TAGS_LIST, empty=False),
	HtmlTag('sub', opt=FULL_TEXT_TAGS_LIST, empty=False),
	HtmlTag('sup', opt=FULL_TEXT_TAGS_LIST, empty=False),
	HtmlTag('code', opt=['', 'b', 'u', 'i', 'em', 'strong'], empty=False),
	HtmlTag('blockquote', opt=FULL_TEXT_TAGS_LIST + ['p', 'code', 'pre', 'cite', 'span', 'ol', 'ul'], empty=False),
	HtmlTag('cite', opt=FULL_TEXT_TAGS_LIST, empty=False),
	HtmlTag('ol', req=['li'], empty=True),
	HtmlTag('ul', req=['li'], empty=True),
	HtmlTag('li', opt=FULL_TEXT_TAGS_LIST + ['ol', 'ul'], empty=None),
	HtmlTag('h1', opt=[''], empty=False),
	HtmlTag('h2', opt=[''], empty=False),
	HtmlTag('h3', opt=[''], empty=False),
	HtmlTag('h4', opt=[''], empty=False),
	HtmlTag('h5', opt=[''], empty=False),
	HtmlTag('h6', opt=[''], empty=False),
	HtmlTag('dl', req=['dt', 'dd'], empty=True),
	HtmlTag('dt', opt=FULL_TEXT_TAGS_LIST, empty=None),
	HtmlTag('dd', opt=FULL_TEXT_TAGS_LIST, empty=None),
	HtmlTag('abbr', opt=[''], req_attributes={'title': ''}, empty=False),
	HtmlTag('img', opt_attributes=['title'], req_attributes={'src': '#', 'alt': ''}, empty=True, attribute_validators = {'src': [HrefValidator()]}),
	HtmlTag('table', opt=['tr', 'caption', 'thead', 'tbody'], empty=True),
	HtmlTag('thead', opt=['tr'], empty=True),
	HtmlTag('tbody', opt=['tr'], empty=True),
	HtmlTag('caption', opt=FULL_TEXT_TAGS_LIST, empty=False),
	HtmlTag('tr', opt=['td', 'th'], empty=True),
	HtmlTag('th', opt=FULL_TEXT_TAGS_LIST, opt_attributes=['colpan', 'rowspan'], attribute_validators={'colspan': [TableSpanValidator()], 'rowspan': [TableSpanValidator()]}, empty=False),
	HtmlTag('td', opt=FULL_TEXT_TAGS_LIST, opt_attributes=['colpan', 'rowspan'], attribute_validators={'colspan': [TableSpanValidator()], 'rowspan': [TableSpanValidator()]}, empty=False),
	HtmlTag('', opt=['', 'a', 'b', 'u', 'br', 'del', 'ins', 'sub', 'sup', 'p', 'i', 'em', 'code', 'strong', 'pre', 'blockquote', 'ol', 'ul', 'span', 'cite', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'abbr', 'dl', 'img', 'table']),
])


class HtmlParser: #pylint: disable=R0902
	# Typy tokenov
	TAG = 1
	ENDTAG = 2
	ENTITY = 3
	WHITESPACE = 4
	TEXT = 5
	SPECIAL = 6
	# Tokenizer
	xmlrx = re.compile(r"""
		<([/]?\w+)       # 1. Tag
		|()/>            # 2. End tag
		|&(\#?\w+);      # 3. Entita
		|(\s+)           # 4. Medzera
		|([^&<>'"=\s]+)  # 5. Text
		|(.)             # 6. Ostatne
	""", re.VERBOSE)
	whitespace_rx = re.compile(r"^\s*$")

	# Validatory tagov
	supported_tags = DEFAULT_TAGS
	# Stav parseru
	TEXT_READ = 1
	TAG_READ = 2
	ATTRIBUTE_SEP_READ = 3
	ATTRIBUTE_START_TEXT_READ = 4
	ATTRIBUTE_TEXT_READ = 5

	auto_paragraphs = True

	def __init__(self, supported_tags = None):
		self.output = StringIO()
		self.errors = []
		if supported_tags is not None:
			self.supported_tags = supported_tags

	def get_attributes(self):
		""" Získanie vlastností parseru pre potreby widgetu """
		return {
			'supported_tags': self.supported_tags
		}

	def get_output(self):
		""" Získanie prečisteného HTML kódu. """
		return self.output.getvalue()

	def __get_token(self):
		""" Ziskanie nasledujúceho tokenu, alebo None. """
		match = self.__tokens.match()
		if not match:
			return None
		return match

	def __get_current_tag(self):
		""" Získanie aktuálneho tagu (posledný tag vo vnorení, alebo rootovský tag). """
		if len(self.__tags) == 0:
			return self.supported_tags['']
		else:
			return self.__tags[-1]

	def __unroll_stack(self):
		if len(self.__tags) < 2:
			return
		if self.__tag_obj.empty is False:
			self.__log_error("Empty tag")
		if self.__tag_obj.req:
			self.__log_error("Required tag")
			for reqtag in self.__tag_obj.req:
				self.__tag_obj = self.supported_tags[reqtag]
				if self.__tag_obj.empty is False:
					self.output.write('<' + reqtag + '/>')
				else:
					self.output.write('<' + reqtag + '>' + reqtag + '</' + reqtag + '>')
		self.output.write('</')
		self.output.write(self.__tags[-1].name)
		self.output.write('>')
		self.__tags.pop()

	def __write_attributes(self):
		to = self.__tags[-1]
		req_attributes = copy.deepcopy(to.req_attributes)
		opt_attributes = copy.deepcopy(to.opt_attributes)
		for attribute in self.__tag_attributes:
			if (not attribute in req_attributes) and (not attribute in opt_attributes):
				self.__log_error("Skipping attribute")
			else:
				av = self.__tag_attributes[attribute]
				validators = to.attribute_validators.get(attribute, [])
				try:
					for validator in validators:
						validator(av[0])
				except ValidationError:
					self.__log_error("Skipping non valid attribute")
					continue
				if attribute in req_attributes:
					del req_attributes[attribute]
				if self.__tag_str.getvalue()[-1] != ' ':
					self.__tag_str.write(' ')
				self.__tag_str.write(attribute + '=' + av[1] + av[0] + av[1])
		for name, value in req_attributes.items():
			self.__log_error("Required attribute")
			if self.__tag_str.getvalue()[-1] != ' ':
				self.__tag_str.write(' ')
			self.__tag_str.write(name + '="' + value + '"')

	def __log_error(self, error):
		""" Zaznamenanie chyby """
		parser_error = ParserError()
		parser_error.message = error
		self.errors.append(parser_error)

	def __tag_start_tag(self, token):
		self.output.write(escape(self.__tag_str.getvalue()))
		self.__tag_str.truncate(0)
		self.__tag_str.seek(0)
		if token[0] == '/':
			self.__endtag = True
			token = token[1:]
			self.__tagname = token
			self.__tag_str.write('</')
			self.__tag_str.write(token)
		else:
			self.__endtag = False
			self.__tagname = token
			self.__tag_str.write('<')
			self.__tag_str.write(token)

	def __tag_end_tag(self, token): #pylint: disable=W0613
		try:
			to = self.supported_tags[self.__tagname]
			if to.empty is False:
				self.__log_error("Empty tag")
				raise KeyError(self.__tagname)
			self.__tags.append(to)
			self.__write_attributes()
			self.__tags.pop()
			self.__tag_str.write(' />')
			self.output.write(self.__tag_str.getvalue())
		except KeyError:
			self.output.write(escape(self.__tag_str.getvalue() + '/>'))
		self.__tag_str.truncate(0)
		self.__tag_str.seek(0)
		self.__state = self.TEXT_READ
		self.__tagname = ''

	def __tag_entity(self, token):
		self.__tag_str.write('&')
		self.__tag_str.write(token)
		self.__tag_str.write(';')
		raise TagReadException()

	def __tag_whitespace(self, token):
		pass

	def __tag_text(self, token):
		attrname = token
		separator = ''
		attrquot = ''
		attrvalue = ''
		attrquotend = ''
		try:
			self.__state = self.ATTRIBUTE_SEP_READ
			while 1:
				match = self.__get_token()
				if not match:
					break
				token_type, token = match.lastindex, match.group(match.lastindex)

				if token_type == self.ENDTAG:
					raise AttributeException()
				elif token_type == self.ENTITY:
					if self.__state == self.ATTRIBUTE_TEXT_READ:
						attrvalue += '&' + token + ';'
					else:
						raise AttributeException()
				elif token_type == self.WHITESPACE:
					if self.__state == self.ATTRIBUTE_SEP_READ or self.ATTRIBUTE_START_TEXT_READ:
						separator += token
					elif self.__state == self.ATTRIBUTE_TEXT_READ:
						attrvalue += token
				elif token_type == self.TEXT:
					if self.__state == self.ATTRIBUTE_TEXT_READ:
						attrvalue += token
					elif self.__state == self.ATTRIBUTE_SEP_READ:
						raise AttributeException()
				elif token_type == self.SPECIAL:
					if self.__state == self.ATTRIBUTE_SEP_READ:
						if token == '=':
							separator += token
							self.__state = self.ATTRIBUTE_START_TEXT_READ
						else:
							raise AttributeException()
					elif self.__state == self.ATTRIBUTE_START_TEXT_READ:
						if token == '"' or token == '"':
							attrquot = token
							self.__state = self.ATTRIBUTE_TEXT_READ
						else:
							raise AttributeException()
					elif self.__state == self.ATTRIBUTE_TEXT_READ:
						if token == attrquot:
							attrquotend = token
							break
						elif token == '<' or token == '>' or token == '&':
							attrvalue += escape(token)
						else:
							attrvalue += token
		except AttributeException:
			self.__tag_str.write(separator)
			self.__tag_str.write(attrquot)
			self.__tag_str.write(attrvalue)
			self.__tag_str.write(attrquotend)
			raise TagReadException()

		self.__state = self.TAG_READ
		if attrname in self.__tag_attributes:
			self.__log_error("Duplicate attribute")
		self.__tag_attributes[attrname] = (attrvalue, attrquot)

	def __tag_special(self, token):
		if token == '>':
			if self.__endtag:
				self.__tag_str.write('>')
				try:
					oldtag = self.__tags[-1].name
					if oldtag == self.__tagname:
						self.__unroll_stack()
						self.__tag_obj = self.__get_current_tag()
					else:
						self.__log_error("Bad end tag")
						can_unroll = False
						for tag in self.__tags:
							if self.__tagname == tag.name:
								can_unroll = True
								break
						if not can_unroll:
							raise KeyError(self.__tagname)
						while self.__tagname != self.__tag_obj.name:
							self.__unroll_stack()
							self.__tag_obj = self.__get_current_tag()
						self.__unroll_stack()
						self.__tag_obj = self.__get_current_tag()
					self.__tag_str.truncate(0)
					self.__tag_str.seek(0)
				except KeyError:
					self.__log_error("Bad end tag")
					self.output.write(escape(self.__tag_str.getvalue()))
					self.__tag_str.truncate(0)
					self.__tag_str.seek(0)
					self.__tagname = ''
				if len(self.__tags) == 1 and self.auto_paragraphs:
					self.__add_auto_paragraph()
			else:
				if self.__tagname not in TEXT_TAGS_LIST:
					self.__trim_empty_tags()
				try:
					to = copy.deepcopy(self.supported_tags[self.__tagname])
					if (not self.__tagname in self.__tag_obj.req) and (not self.__tagname in self.__tag_obj.opt):
						self.__log_error("Missing end tag")
						can_unroll = False
						for tag in self.__tags:
							if (self.__tagname in tag.req) or (self.__tagname in tag.opt):
								can_unroll = True
								break
						if not can_unroll:
							raise KeyError(self.__tagname)
						while (not self.__tagname in self.__tag_obj.req) and (not self.__tagname in self.__tag_obj.opt):
							self.__unroll_stack()
							self.__tag_obj = self.__get_current_tag()
					try:
						self.__tag_obj.req.remove(self.__tagname)
						self.__tag_obj.opt.add(self.__tagname)
					except KeyError:
						pass
					self.__tags.append(to)
					self.__write_attributes()
					# Zápis atribútov
					self.__tag_str.write('>')
					self.output.write(self.__tag_str.getvalue())
					self.__tag_attributes = OrderedDict()
					self.__tag_str.truncate(0)
					self.__tag_str.seek(0)
					self.__tag_obj = to
				# Nepodporovany tag
				except KeyError:
					self.__log_error("Unknown tag")
					self.__tag_str.write('>')
					self.output.write(escape(self.__tag_str.getvalue()))
					self.__tag_str.truncate(0)
					self.__tag_str.seek(0)
					self.__state = self.TEXT_READ
			self.__tag_obj = self.__get_current_tag()
		else:
			self.__log_error("Bad token")
			raise TagReadException()
		self.__state = self.TEXT_READ
		self.__tagname = ''

	def __read_tag(self, match):
		type, token = match.lastindex, match.group(match.lastindex)
		if type == self.TAG:
			self.__tag_start_tag(token)
		elif type == self.ENDTAG:
			self.__tag_end_tag(token)
		elif type == self.ENTITY:
			self.__tag_entity(token)
		elif type == self.WHITESPACE:
			self.__tag_whitespace(token)
		elif type == self.TEXT:
			self.__tag_text(token)
		elif type == self.SPECIAL:
			self.__tag_special(token)

	def __add_auto_paragraph(self):
		if self.auto_paragraphs:
			paragraph = copy.deepcopy(self.supported_tags['p'])
			paragraph.trim_empty = True
			paragraph.pos = self.output.tell()
			self.__tags.append(paragraph)
			self.output.write("<p>")

	def __trim_empty_tags(self):
		if self.__tags and self.__tags[-1].trim_empty:
			self.output.seek(self.__tags[-1].pos)
			part = self.output.read()
			if not self.whitespace_rx.match(part[3:]):
				return
			self.output.truncate(self.__tags[-1].pos)
			self.output.seek(self.__tags[-1].pos)
			self.output.write(part[3:])
			self.__tags.pop()

	def __set_tag_stack_noempty(self):
		if self.__tag_obj != '' and self.__tag_obj.empty is False:
			for tag in self.__tags:
				tag.empty = None

	""" Spracovanie HTML kódu. """
	def parse(self, code):
		code = code.replace("\r\n", "\n")
		# Vyčistenie výstupného bufferu
		self.output.truncate(0)
		self.output.seek(0)
		self.errors = []
		# Dáta aktuálneho tagu
		self.__tag_str = StringIO()
		# Aktuálny tag
		self.__tag_obj = copy.deepcopy(self.supported_tags[''])
		# Ak je tag ukončovací má hodnotu True
		self.__endtag = False
		# Názov aktuálneho tagu (relevantné len v stave čítania tagu)
		self.__tagname = ''
		# Zázobník názvov tagov
		self.__tags = [self.supported_tags['']]
		# Tokenizer skenujúci pomocou regulárnych výrazov
		self.__tokens = self.xmlrx.scanner(code)
		# Atribút aktuálneho tagu
		self.__tag_attributes = OrderedDict()

		# Čítanie súboru
		self.__state = self.TEXT_READ
		self.__add_auto_paragraph()
		while 1:
			match = self.__get_token()
			if not match:
				break

			# Čítanie v priestore medzi tagmi
			if self.__state == self.TEXT_READ:
				type, token = match.lastindex, match.group(match.lastindex)
				if type == self.TAG:
					self.__state = self.TAG_READ
					if token[0] == '/':
						self.__endtag = True
						token = token[1:]
						self.__tagname = token
						self.__tag_str.write('</')
						self.__tag_str.write(token)
					else:
						self.__endtag = False
						self.__tagname = token
						self.__tag_str.write('<')
						self.__tag_str.write(token)
				if type == self.ENDTAG:
					self.output.write('/&gt;')
				elif type == self.WHITESPACE:
					auto_paragraph = False
					if self.auto_paragraphs and len(self.__tags) == 2 and self.__tags[1].trim_empty and token == "\n\n":
						auto_paragraph = True
						self.__unroll_stack()
					self.output.write(token)
					if auto_paragraph:
						self.__add_auto_paragraph()
				if (type == self.ENTITY) or (type == self.TEXT) or (type == self.SPECIAL):
					if self.__tag_obj.empty is True:
						self.__log_error("No content allowed")
						while self.__tag_obj.empty is True:
							self.__unroll_stack()
							self.__tag_obj = self.__get_current_tag()
					if type == self.ENTITY:
						self.output.write('&' + token + ';')
					elif type == self.TEXT:
						self.output.write(token)
					elif type == self.SPECIAL:
						self.output.write(escape(token))
					self.__set_tag_stack_noempty()

			# Čítanie vnútra tagov
			elif self.__state == self.TAG_READ:
				try:
					self.__read_tag(match)
				except TagReadException:
					self.output.write(escape(self.__tag_str.getvalue()))
					self.__tag_str.truncate(0)
					self.__tag_str.seek(0)
					self.__state = self.TEXT_READ
		self.__trim_empty_tags()
		# Uzatvorenie neuzatvorenych tagov
		while len(self.__tags) > 1:
			self.__log_error("Tag not closed")
			self.__unroll_stack()
			self.__tag_obj = self.__get_current_tag()


class RawParser:
	def parse(self, text):
		self.output = text

	def get_output(self):
		return self.output

	def get_attributes(self):
		return {}


class TextParser:
	def parse(self, text):
		self.output = linebreaks_filter(escape(text))

	def get_output(self):
		return self.output

	def get_attributes(self):
		return {}
