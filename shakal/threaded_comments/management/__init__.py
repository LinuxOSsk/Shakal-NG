# -*- coding: utf-8 -*-

from copy import deepcopy
from django.contrib.contenttypes.models import ContentType
from django.db import connections
from django.db.models.signals import post_syncdb
from shakal.threaded_comments import models


def install_view(connection, source_table, join_tables, extra_columns, content_type_id, reverse = False):
	query = 'CREATE OR REPLACE VIEW ' + source_table + ('reverse' if reverse else '') + 'view AS SELECT '
	final_columns = [source_table + '.*']
	tables = zip(deepcopy(join_tables), deepcopy(extra_columns))
	for table in tables:
		columns = table[1]
		for alias in columns:
			columns[alias] = table[0] + '.' + columns[alias]
		final_columns += map(lambda t: t[1] + ' AS ' + t[0], columns.items())
	query += ', '.join(final_columns)
	if reverse:
		query += ' FROM ' + join_tables[0]
	else:
		query += ' FROM ' + source_table
	for table in join_tables:
		if reverse:
			query += ' INNER JOIN ' + source_table + ' ON ('
			reverse = False
		else:
			query += ' LEFT OUTER JOIN ' + table + ' ON ('
		query += source_table + '.id = ' + table + '.object_id AND '
		query += table + '.content_type_id = ' + str(content_type_id) + ')'
	connection.cursor().execute(query)


def install_views(sender, **kwargs):
	connection = connections[kwargs['db']]
	join_tables = ['threaded_comments_rootheader']
	extra_columns = [{'comment_count': 'comment_count', 'last_comment': 'last_comment'}]
	join_tables_hitcount = join_tables + ['hitcount_hitcount']
	extra_columns_hitcount = extra_columns + [{'display_count': 'hits'}]
	if connection.vendor == 'postgresql':
		install_view(connection,
			'article_article',
			join_tables_hitcount,
			extra_columns_hitcount,
			ContentType.objects.get(app_label = 'article', model = 'article').pk
		)
		install_view(connection,
			'forum_topic',
			join_tables,
			extra_columns,
			ContentType.objects.get(app_label = 'forum', model = 'topic').pk,
			reverse = True
		)
		install_view(connection,
			'forum_topic',
			join_tables,
			extra_columns,
			ContentType.objects.get(app_label = 'forum', model = 'topic').pk,
		)
		install_view(connection,
			'news_news',
			join_tables,
			extra_columns,
			ContentType.objects.get(app_label = 'news', model = 'news').pk
		)
		install_view(connection,
			'survey_survey',
			join_tables,
			extra_columns,
			ContentType.objects.get(app_label = 'survey', model = 'survey').pk
		)


post_syncdb.connect(install_views, sender = models)
