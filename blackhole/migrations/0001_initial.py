# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import rich_editor.fields
import mptt.fields


class Migration(migrations.Migration):

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='Node',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(verbose_name='vytvoren\xe9', editable=False)),
				('updated', models.DateTimeField(verbose_name='upraven\xe9', editable=False)),
				('title', models.CharField(max_length=128)),
				('is_published', models.BooleanField(default=False)),
				('is_commentable', models.BooleanField(default=True)),
				('is_promoted', models.BooleanField(default=False)),
				('is_sticky', models.BooleanField(default=False)),
				('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
			],
			options={
				'abstract': False,
			},
		),
		migrations.CreateModel(
			name='NodeRevision',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('title', models.CharField(max_length=128)),
				('original_body', rich_editor.fields.RichTextOriginalField(property_name='body', filtered_field='filtered_body')),
				('filtered_body', rich_editor.fields.RichTextFilteredField(editable=False)),
				('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
				('node', models.ForeignKey(to='blackhole.Node')),
			],
		),
		migrations.CreateModel(
			name='Term',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('name', models.CharField(max_length=255)),
				('description', models.TextField()),
				('lft', models.PositiveIntegerField(editable=False, db_index=True)),
				('rght', models.PositiveIntegerField(editable=False, db_index=True)),
				('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
				('level', models.PositiveIntegerField(editable=False, db_index=True)),
				('parent', mptt.fields.TreeForeignKey(related_name='children', blank=True, to='blackhole.Term', null=True)),
			],
			options={
				'abstract': False,
			},
		),
		migrations.CreateModel(
			name='VocabularyNodeType',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('name', models.CharField(max_length=32, db_column='type')),
			],
		),
		migrations.AddField(
			model_name='term',
			name='vocabulary',
			field=models.ForeignKey(to='blackhole.VocabularyNodeType', db_column='vid'),
		),
		migrations.AddField(
			model_name='node',
			name='revision',
			field=models.ForeignKey(related_name='revisions', to='blackhole.NodeRevision'),
		),
		migrations.AddField(
			model_name='node',
			name='vocabulary',
			field=models.ForeignKey(to='blackhole.VocabularyNodeType'),
		),
	]
