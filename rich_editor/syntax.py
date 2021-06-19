# -*- coding: utf-8 -*-
import re

from django.template.defaultfilters import striptags

from fulltext.templatetags.html_entity_decode import html_entity_decode_char, xml_entity_decode_char


LEXERS = (
	('ada', 'ADA'),
	('apacheconf', 'ApacheConf'),
	('awk', 'Awk'),
	('bash', 'Bash'),
	('csharp', 'C#'),
	('cpp', 'C++'),
	('c', 'C'),
	('cmake', 'CMake'),
	('css', 'CSS'),
	('clojure', 'Clojure'),
	('clojurescript', 'ClojureScript'),
	('coffee', 'CoffeeScript'),
	('cl', 'Common Listp'),
	('d', 'D'),
	('dart', 'Dart'),
	('diff', 'Diff'),
	('django', 'Django/Jinja'),
	('eiffel', 'Eiffel'),
	('erlang', 'Erlang'),
	('fortran', 'Fortran'),
	('glsl', 'GLSL'),
	('go', 'Go'),
	('groovy', 'Groovy'),
	('html', 'HTML'),
	('haskell', 'Haskell'),
	('json', 'JSON'),
	('java', 'Java'),
	('js', 'JavaScript'),
	('lua', 'Lua'),
	('mak', 'Makefile'),
	('mysql', 'MySQL'),
	('ocaml', 'OCaml'),
	('pas', 'Pascal'),
	('php', 'PHP'),
	('plsql', 'PL/pgSQL'),
	('perl', 'Perl'),
	('python', 'Python'),
	('qml', 'QML'),
	('ruby', 'Ruby'),
	('rust', 'Rust'),
	('scala', 'Scala'),
	('scheme', 'Scheme'),
	('smalltalk', 'Smalltalk'),
	('tcl', 'Tcl'),
	('tex', 'TeX'),
	('ts', 'TypeScript'),
	('xml', 'XML'),
	('xquery', 'XQuery'),
	('xslt', 'XSLT'),
	('vhdl', 'vhdl'),
)


ENTITY_PATTERN = re.compile(r'&(\w+?);')
DECIMAL_ENTITY_PATTERN = re.compile(r'&\#(\d+?);')


def html_entity_decode(string):
	without_entity = ENTITY_PATTERN.sub(html_entity_decode_char, string)
	return DECIMAL_ENTITY_PATTERN.sub(xml_entity_decode_char, without_entity)


def format_code(code, lang):
	import pygments
	from pygments import lexers, formatters, util

	if not lang in dict(LEXERS):
		return None

	if len(code) > 200000:
		return None
	code = code.replace('\t', '    ')

	try:
		lexer = lexers.get_lexer_by_name(lang)
	except util.ClassNotFound:
		return None

	formatter = formatters.get_formatter_by_name('html')
	formatter.nowrap = True

	return pygments.highlight(code, lexer, formatter)


def highlight_block(match):
	lang = match.group(2)
	code = format_code(html_entity_decode(striptags(match.group(3))), lang)
	if code is None:
		return ''.join((match.group(1), match.group(3), match.group(4)))
	else:
		return match.group(1) + code + match.group(4)


def highlight_pre_blocks(html):
	return re.sub(r'(<pre\s+class="code-([^"]+)">)(.*?)(</\s*pre>)', highlight_block, html, flags=re.DOTALL)
