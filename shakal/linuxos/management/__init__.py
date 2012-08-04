# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.db import connections
from django.db.models.signals import post_syncdb
from shakal.threaded_comments import models


def install_view(connection, source_table, join_tables, extra_columns, content_type_id):
	query = 'CREATE OR REPLACE VIEW ' + source_table + 'view AS SELECT '
	final_columns = [source_table + '.*']
	tables = zip(join_tables, extra_columns)
	for table in tables:
		columns = table[1]
		for alias in columns:
			columns[alias] = table[0] + '.' + columns[alias]
		final_columns += map(lambda t: t[1] + ' AS ' + t[0], columns.items())
	query += ', '.join(final_columns)
	query += ' FROM ' + source_table
	for table in join_tables:
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
			ContentType.objects.get(app_label = 'article', model = 'articleview').pk
		)
		install_view(connection,
			'forum_topic',
			join_tables,
			extra_columns,
			ContentType.objects.get(app_label = 'forum', model = 'topicview').pk
		)


post_syncdb.connect(install_views, sender = models)
