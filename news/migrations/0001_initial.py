# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_autoslugfield.fields
import django.db.models.deletion
import rich_editor.fields
from django.conf import settings


class Migration(migrations.Migration):

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='News',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(verbose_name='vytvoren\xe9', editable=False)),
				('updated', models.DateTimeField(verbose_name='upraven\xe9', editable=False)),
				('title', models.CharField(max_length=255, verbose_name='titulok')),
				('slug', django_autoslugfield.fields.AutoSlugField(unique=True)),
				('original_short_text', rich_editor.fields.RichTextOriginalField(max_length=3000, verbose_name='kr\xe1tky text', property_name='short_text', filtered_field='filtered_short_text')),
				('filtered_short_text', rich_editor.fields.RichTextFilteredField(editable=False)),
				('original_long_text', rich_editor.fields.RichTextOriginalField(verbose_name='dlh\xfd text', property_name='long_text', filtered_field='filtered_long_text')),
				('filtered_long_text', rich_editor.fields.RichTextFilteredField(editable=False)),
				('authors_name', models.CharField(max_length=255, verbose_name='meno authora')),
				('source', models.CharField(max_length=100, verbose_name='zdroj', blank=True)),
				('source_url', models.URLField(max_length=1000, verbose_name='URL zdroja', blank=True)),
				('approved', models.BooleanField(default=False, verbose_name='schv\xe1len\xe1')),
				('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='author', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
			],
			options={
				'verbose_name': 'spr\xe1va',
				'verbose_name_plural': 'spr\xe1vy',
			},
		),
	]
