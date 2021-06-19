# -*- coding: utf-8 -*-
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
			name='File',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('filename', models.CharField(max_length=255)),
				('filepath', models.FileField(upload_to='blackhole')),
				('filemime', models.CharField(max_length=255)),
				('filesize', models.IntegerField()),
			],
		),
		migrations.CreateModel(
			name='Node',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(editable=False)),
				('updated', models.DateTimeField(editable=False)),
				('node_type', models.CharField(max_length=32)),
				('title', models.CharField(max_length=128)),
				('is_published', models.BooleanField(default=False, blank=True)),
				('is_commentable', models.BooleanField(default=True, blank=True)),
				('is_promoted', models.BooleanField(default=False, blank=True)),
				('is_sticky', models.BooleanField(default=False, blank=True)),
				('author', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
			],
			options={
				'verbose_name': 'blackhole \u010dl\xe1nok',
				'verbose_name_plural': 'blackhole \u010dl\xe1nky',
			},
		),
		migrations.CreateModel(
			name='NodeRevision',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(editable=False)),
				('updated', models.DateTimeField(editable=False)),
				('title', models.CharField(max_length=128)),
				('original_body', rich_editor.fields.RichTextOriginalField(property_name='body', filtered_field='filtered_body')),
				('filtered_body', rich_editor.fields.RichTextFilteredField(editable=False)),
				('log', models.TextField(blank=True)),
				('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
				('node', models.ForeignKey(to='blackhole.Node', on_delete=models.CASCADE)),
			],
			options={
				'abstract': False,
			},
		),
		migrations.CreateModel(
			name='Term',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('name', models.CharField(max_length=255)),
				('description', models.TextField()),
				('lft', models.PositiveIntegerField(editable=False, db_index=True)),
				('rght', models.PositiveIntegerField(editable=False, db_index=True)),
				('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
				('level', models.PositiveIntegerField(editable=False, db_index=True)),
				('parent', mptt.fields.TreeForeignKey(related_name='children', blank=True, to='blackhole.Term', null=True, on_delete=models.CASCADE)),
			],
			options={
				'abstract': False,
			},
		),
		migrations.CreateModel(
			name='VocabularyNodeType',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('name', models.CharField(max_length=32, db_column='type')),
			],
		),
		migrations.AddField(
			model_name='term',
			name='vocabulary',
			field=models.ForeignKey(to='blackhole.VocabularyNodeType', db_column='vid', on_delete=models.CASCADE),
		),
		migrations.AddField(
			model_name='node',
			name='revision',
			field=models.ForeignKey(related_name='revisions', to='blackhole.NodeRevision', on_delete=models.CASCADE),
		),
		migrations.AddField(
			model_name='node',
			name='terms',
			field=models.ManyToManyField(to='blackhole.Term', blank=True),
		),
		migrations.AddField(
			model_name='file',
			name='node',
			field=models.ForeignKey(to='blackhole.Node', on_delete=models.CASCADE),
		),
	]
