# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_autoslugfield.fields
import django.db.models.deletion
from django.conf import settings
import rich_editor.fields


class Migration(migrations.Migration):

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='Category',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('name', models.CharField(max_length=255, verbose_name='n\xe1zov')),
				('slug', models.SlugField(unique=True)),
				('description', models.TextField(verbose_name='popis')),
			],
			options={
				'verbose_name': 'kateg\xf3ria',
				'verbose_name_plural': 'kateg\xf3rie',
			},
		),
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
				('original_long_text', rich_editor.fields.RichTextOriginalField(help_text='Vypl\u0148te v pr\xedpade, \u017ee sa text v detaile spr\xe1vy m\xe1 l\xed\u0161i\u0165 od textu v zozname.', verbose_name='dlh\xfd text', property_name='long_text', filtered_field='filtered_long_text')),
				('filtered_long_text', rich_editor.fields.RichTextFilteredField(editable=False)),
				('authors_name', models.CharField(max_length=255, verbose_name='meno autora')),
				('source', models.CharField(max_length=100, verbose_name='zdroj', blank=True)),
				('source_url', models.URLField(max_length=1000, verbose_name='URL zdroja', blank=True)),
				('approved', models.BooleanField(default=False, verbose_name='schv\xe1len\xe1')),
				('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='autor', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
				('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='kateg\xf3ria', to='news.Category')),
			],
			options={
				'verbose_name': 'spr\xe1va',
				'verbose_name_plural': 'spr\xe1vy',
			},
		),
	]
