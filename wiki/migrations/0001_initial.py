# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_autoslugfield.fields
from django.conf import settings
import rich_editor.fields


class Migration(migrations.Migration):

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='Page',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(verbose_name='vytvoren\xe9', editable=False)),
				('updated', models.DateTimeField(verbose_name='upraven\xe9', editable=False)),
				('title', models.CharField(max_length=255, verbose_name='titulok')),
				('slug', django_autoslugfield.fields.AutoSlugField(unique=True, verbose_name='slug')),
				('original_text', rich_editor.fields.RichTextOriginalField(property_name='text', filtered_field='filtered_text')),
				('filtered_text', rich_editor.fields.RichTextFilteredField(editable=False)),
				('page_type', models.CharField(default='p', max_length=1, verbose_name='typ str\xe1nky', choices=[('h', 'Domovsk\xe1 str\xe1nka'), ('i', 'Intern\xe1 str\xe1nka'), ('p', 'Str\xe1nka wiki')])),
				('lft', models.PositiveIntegerField(editable=False, db_index=True)),
				('rght', models.PositiveIntegerField(editable=False, db_index=True)),
				('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
				('level', models.PositiveIntegerField(editable=False, db_index=True)),
				('last_author', models.ForeignKey(verbose_name='posledn\xfd autor', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
				('parent', models.ForeignKey(related_name='children', verbose_name='nadraden\xe1 str\xe1nka', blank=True, to='wiki.Page', null=True)),
			],
			options={
				'verbose_name': 'Wiki str\xe1nka',
				'verbose_name_plural': 'Wiki str\xe1nky',
			},
		),
	]
