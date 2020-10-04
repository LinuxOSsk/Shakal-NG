# -*- coding: utf-8 -*-
import psycopg2
from django.contrib.postgres.search import SearchQuery
from django.db.models import Func, TextField, Expression, Value


class SearchConfig(Expression):
	def __init__(self, config):
		super().__init__()
		if not hasattr(config, 'resolve_expression'):
			config = Value(config)
		self.config = config

	@classmethod
	def from_parameter(cls, config):
		if config is None or isinstance(config, cls):
			return config
		return cls(config)

	def get_source_expressions(self):
		return [self.config]

	def set_source_expressions(self, exprs):
		self.config, = exprs

	def as_sql(self, compiler, connection):
		sql, params = compiler.compile(self.config)
		return '%s::regconfig' % sql, params


class SearchHeadline(Func):
	function = 'ts_headline'
	template = '%(function)s(%(expressions)s%(options)s)'
	output_field = TextField()

	def __init__(
		self, expression, query, *, config=None, start_sel=None, stop_sel=None,
		max_words=None, min_words=None, short_word=None, highlight_all=None,
		max_fragments=None, fragment_delimiter=None,
	):
		if not hasattr(query, 'resolve_expression'):
			query = SearchQuery(query)
		options = {
			'StartSel': start_sel,
			'StopSel': stop_sel,
			'MaxWords': max_words,
			'MinWords': min_words,
			'ShortWord': short_word,
			'HighlightAll': highlight_all,
			'MaxFragments': max_fragments,
			'FragmentDelimiter': fragment_delimiter,
		}
		self.options = {
			option: value
			for option, value in options.items() if value is not None
		}
		expressions = (expression, query)
		if config is not None:
			config = SearchConfig.from_parameter(config)
			expressions = (config,) + expressions
		super().__init__(*expressions)

	def as_sql(self, compiler, connection, function=None, template=None):
		options_sql = ''
		options_params = []
		if self.options:
			# getquoted() returns a quoted bytestring of the adapted value.
			options_params.append(', '.join(
				'%s=%s' % (
					option,
					psycopg2.extensions.adapt(value).getquoted().decode(),
				) for option, value in self.options.items()
			))
			options_sql = ', %s'
		sql, params = super().as_sql(
			compiler, connection, function=function, template=template,
			options=options_sql,
		)
		return sql, params + options_params


if not 'websearch' in SearchQuery.SEARCH_TYPES:
	SearchQuery.SEARCH_TYPES = {
		'plain': 'plainto_tsquery',
		'phrase': 'phraseto_tsquery',
		'raw': 'to_tsquery',
		'websearch': 'websearch_to_tsquery',
	}
