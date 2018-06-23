# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import rich_editor.fields


class Migration(migrations.Migration):

	dependencies = [
		('contenttypes', '0002_remove_content_type_name'),
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='Note',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(verbose_name='vytvoren\xe9', editable=False)),
				('updated', models.DateTimeField(verbose_name='upraven\xe9', editable=False)),
				('object_id', models.PositiveIntegerField(verbose_name='id objektu')),
				('subject', models.CharField(max_length=100, verbose_name='predmet')),
				('authors_name', models.CharField(max_length=255, verbose_name='meno autora')),
				('original_text', rich_editor.fields.RichTextOriginalField(max_length=20000, verbose_name='pozn\xe1mka', property_name='text', filtered_field='filtered_text')),
				('filtered_text', rich_editor.fields.RichTextFilteredField(editable=False)),
				('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='autor', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
				('content_type', models.ForeignKey(verbose_name='typ obsahu', to='contenttypes.ContentType', on_delete=models.CASCADE)),
			],
			options={
				'verbose_name': 'pozn\xe1mka',
				'verbose_name_plural': 'pozn\xe1mky',
			},
		),
	]
