# -*- coding: utf-8 -*-
import re
import StringIO
import copy
from django.utils.html import escape

class AttributeException(Exception):
	pass
class TagReadException(Exception):
	pass
class ParserError(object):
	def __init__(self):
		self.message = ''

class HtmlTag:
	def __init__(self, name, req = [], opt = [], req_attributes = [], opt_attributes = [], attribute_validators = {}, empty = None):
		self.name = name
		self.req = set(req)
		self.opt = set(opt)
		self.req_attributes = set(req_attributes)
		self.opt_attributes = set(opt_attributes)
		self.attribute_validators = attribute_validators
		self.empty = empty

	def get_child_tags(self):
		return self.req.union(self.opt)

ALL_TAGS = ['a', 'abbr', 'acronym', 'address', 'applet', 'area', 'article', 'aside', 'audio', 'b', 'base', 'basefont', 'bdi', 'bdo', 'big', 'blockquote', 'body', 'br', 'button', 'canvas', 'caption', 'center', 'cite', 'code', 'col', 'colgroup', 'command', 'datalist', 'dd', 'del', 'details', 'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'embed', 'fieldset', 'figcaption', 'figure', 'font', 'footer', 'form', 'frame', 'frameset', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'header', 'hgroup', 'hr', 'html', 'i', 'iframe', 'img', 'input', 'ins', 'kbd', 'keygen', 'label', 'legend', 'li', 'link', 'map', 'mark', 'menu', 'meta', 'meter', 'nav', 'noframes', 'noscript', 'object', 'ol', 'optgroup', 'option', 'output', 'p', 'param', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby', 's', 'samp', 'script', 'section', 'select', 'small', 'source', 'span', 'strike', 'strong', 'style', 'sub', 'summary', 'sup', 'table', 'tbody', 'td', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title', 'tr', 'track', 'tt', 'u', 'ul', 'var', 'video', 'wbr']


TEXT_TAGS = ['', 'b', 'u', 'i', 'em', 'strong', 'a', 'br']


class HtmlParser:
	# Typy tokenov
	TAG = 1; ENDTAG = 2; ENTITY = 3; WHITESPACE = 4; TEXT = 5; SPECIAL = 6;
	# Tokenizer
	xmlrx = re.compile(r"""
		<([/]?\w+)       # 1. Tag
		|()/>            # 2. End tag
		|&(\#?\w+);      # 3. Entita
		|(\s+)           # 4. Medzera
		|([^&<>'"=\s]+)  # 5. Text
		|(.)             # 6. Ostatne
	""", re.VERBOSE)

	# Validatory tagov
	supported_tags = {
		'b'          : HtmlTag('b', opt = TEXT_TAGS, empty = False),
		'u'          : HtmlTag('u', opt = TEXT_TAGS, empty = False),
		'i'          : HtmlTag('i', opt = TEXT_TAGS, empty = False),
		'em'         : HtmlTag('em', opt = TEXT_TAGS, empty = False),
		'strong'     : HtmlTag('strong', opt = TEXT_TAGS, empty = False),
		'a'          : HtmlTag('a', opt = [''], req_attributes = ['href'], empty = False),
		'pre'        : HtmlTag('pre', opt = [''], empty = False),
		'p'          : HtmlTag('p', opt = TEXT_TAGS + ['span', 'code', 'cite'], empty = False),
		'span'       : HtmlTag('span', opt = TEXT_TAGS, empty = False),
		'br'         : HtmlTag('br', empty = True),
		'code'       : HtmlTag('p', opt = ['', 'b', 'u', 'i', 'em', 'strong'], empty = False),
		'blockquote' : HtmlTag('blockquote', opt = TEXT_TAGS + ['p', 'code', 'pre', 'cite', 'span', 'ol', 'ul'], empty = False),
		'cite'       : HtmlTag('cite', opt = TEXT_TAGS, empty = False),
		'ol'         : HtmlTag('ol', req = ['li'], empty = True),
		'ul'         : HtmlTag('ul', req = ['li'], empty = True),
		'li'         : HtmlTag('li', opt = TEXT_TAGS + ['ol', 'ul'], empty = None),
		''           : HtmlTag('', opt = ['', 'a','b','u', 'br','p','i','em','code','strong','pre','blockquote','ol','ul','span','cite'])
	}
	# Stav parseru
	TEXT_READ = 1; TAG_READ = 2; ATTRIBUTE_SEP_READ = 3; ATTRIBUTE_START_TEXT_READ = 4; ATTRIBUTE_TEXT_READ = 5;

	def __init__(self):
		self.output = StringIO.StringIO()
		self.errors = []

	""" Získanie prečisteného HTML kódu. """
	def get_output(self):
		return self.output.getvalue()

	""" Ziskanie nasledujúceho tokenu, alebo None. """
	def __get_token(self):
		match = self.__tokens.match()
		if not match:
			return None
		return match

	""" Získanie aktuálneho tagu (posledný tag vo vnorení, alebo rootovský tag). """
	def __get_current_tag(self):
		if len(self.__tags) == 0:
			return self.supported_tags['']
		else:
			return self.__tags[-1]

	def __unroll_stack(self):
		if self.__tag_obj.empty == False:
			self.__log_error("Empty tag")
			self.output.write("&nbsp;")
		if self.__tag_obj.req:
			self.__log_error("Required tag")
			for reqtag in self.__tag_obj.req:
				self.__tag_obj = self.supported_tags[reqtag]
				if self.__tag_obj.empty == False:
					self.output.write('<' + reqtag + '/>')
				else:
					self.output.write('<' + reqtag + '>' + reqtag + '</' + reqtag + '>')
		self.output.write('</')
		self.output.write(self.__tags[-1].name)
		self.output.write('>')
		self.__tags.pop()

	""" Zaznamenanie chyby """
	def __log_error(self, error):
		parser_error = ParserError()
		parser_error.error = error
		self.errors.append(parser_error)

	def __read_tag(self, match):
		type, token = match.lastindex, match.group(match.lastindex)
		if type == self.TAG:
			self.output.write(escape(self.__tag_str.getvalue()))
			self.__tag_str.truncate(0)
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
			try:
				to = self.supported_tags[self.__tagname]
				if to.empty == False:
					self.__log_error("Empty tag")
					raise KeyError(self.__tagname);
				self.__tag_str.write('/>')
				self.output.write(self.__tag_str.getvalue())
			except:
				self.output.write(escape(self.__tag_str.getvalue() + '/>'))
			self.__tag_str.truncate(0)
			self.__state = self.TEXT_READ
			self.__tagname = ''
		elif type == self.ENTITY:
			self.__tag_str.write('&')
			self.__tag_str.write(token)
			self.__tag_str.write(';')
			raise TagReadException()
		elif type == self.WHITESPACE:
			self.__tag_str.write(token)
		# tutaj
		elif type == self.TEXT:
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
					type, token = match.lastindex, match.group(match.lastindex)

					if type == self.ENDTAG:
						raise AttributeException()
					elif type == self.ENTITY:
						if self.__state == self.ATTRIBUTE_TEXT_READ:
							attrvalue += token
						else:
							raise AttributeException()
					elif type == self.WHITESPACE:
						if self.__state == self.ATTRIBUTE_SEP_READ or self.ATTRIBUTE_START_TEXT_READ:
							separator += token
						elif self.__state == self.ATTRIBUTE_TEXT_READ:
							attrvalue += token
					elif type == self.TEXT:
						if self.__state == self.ATTRIBUTE_TEXT_READ:
							attrvalue += token
						elif self.__state == self.ATTRIBUTE_SEP_READ:
							raise AttributeException()
					elif type == self.SPECIAL:
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

		elif type == self.SPECIAL:
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
					except:
						self.__log_error("Bad end tag")
						self.output.write(escape(self.__tag_str.getvalue()))
						self.__tag_str.truncate(0)
						self.__tagname = ''
				else:
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
						for attribute in self.__tag_attributes:
							if (not attribute in to.req_attributes) and (not attribute in to.opt_attributes):
								self.__log_error("Skipping attribute")
							else:
								if attribute in to.req_attributes:
									to.req_attributes.remove(attribute)
								av = self.__tag_attributes[attribute]
								self.__tag_str.write(attribute + '=' + av[1] + av[0] + av[1])
						for attribute in to.req_attributes:
							self.__log_error("Required attribute")
							self.__tag_str.write(' ' + attribute + '=""')
						# Zápis atribútov
						self.__tag_str.write('>')
						self.output.write(self.__tag_str.getvalue())
						self.__tag_attributes = {}
						self.__tag_str.truncate(0)
						self.__tag_obj= to
					# Nepodporovany tag
					except:
						self.__log_error("Unknown tag")
						self.__tag_str.write('>')
						self.output.write(escape(self.__tag_str.getvalue()))
						self.__tag_str.truncate(0)
						self.__state = self.TEXT_READ
				self.__tag_obj = self.__get_current_tag()
			else:
				self.__log_error("Bad token")
				raise TagReadException()
			self.__state = self.TEXT_READ
			self.__tagname = ''

	""" Spracovanie HTML kódu. """
	def parse(self, code):
		# Vyčistenie výstupného bufferu
		self.output.truncate(0)
		# Dáta aktuálneho tagu
		self.__tag_str = StringIO.StringIO()
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
		self.__tag_attributes = {}



		# Čítanie súboru
		self.__state = self.TEXT_READ
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
					self.output.write(token)
				if (type == self.ENTITY) or (type == self.TEXT) or (type == self.SPECIAL):
					if self.__tag_obj.empty == True:
						self.__log_error("No content allowed")
						while self.__tag_obj.empty == True:
							self.__unroll_stack()
							self.__tag_obj = self.__get_current_tag()
					if type == self.ENTITY:
						self.output.write('&' + token + ';')
					elif type == self.TEXT:
						self.output.write(token)
					elif type == self.SPECIAL:
						self.output.write(escape(token))
					if self.__tag_obj != '' and self.__tag_obj.empty == False:
						self.__tag_obj.empty = None

			# Čítanie vnútra tagov
			elif self.__state == self.TAG_READ:
				try:
					self.__read_tag(match)
				except TagReadException:
					self.output.write(escape(self.__tag_str.getvalue()))
					self.__tag_str.truncate(0)
					self.__state = self.TEXT_READ
		# Uzatvorenie neuzatvorenych tagov
		while len(self.__tags) > 1:
			self.__log_error("Tag not closed")
			self.__unroll_stack()
			self.__tag_obj = self.__get_current_tag()
