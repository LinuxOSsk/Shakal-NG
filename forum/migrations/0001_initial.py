# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import rich_editor.fields


class Migration(migrations.Migration):

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='Section',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('name', models.CharField(max_length=255, verbose_name='n\xe1zov')),
				('slug', models.SlugField(unique=True)),
				('description', models.TextField(verbose_name='popis')),
			],
			options={
				'verbose_name': 'sekcia',
				'verbose_name_plural': 'sekcie',
			},
		),
		migrations.CreateModel(
			name='Topic',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(verbose_name='vytvoren\xe9', editable=False)),
				('updated', models.DateTimeField(verbose_name='upraven\xe9', editable=False)),
				('title', models.CharField(max_length=100, verbose_name='predmet')),
				('original_text', rich_editor.fields.RichTextOriginalField(max_length=3000, verbose_name='text', property_name='text', filtered_field='filtered_text')),
				('filtered_text', rich_editor.fields.RichTextFilteredField(editable=False)),
				('authors_name', models.CharField(max_length=50, verbose_name='meno autora')),
				('is_removed', models.BooleanField(default=False, verbose_name='vymazan\xe9')),
				('is_resolved', models.BooleanField(default=False, verbose_name='vyrie\u0161en\xe9')),
				('author', models.ForeignKey(verbose_name='autor', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
				('section', models.ForeignKey(verbose_name='sekcia', to='forum.Section', on_delete=models.CASCADE)),
			],
			options={
				'verbose_name': 't\xe9ma vo f\xf3re',
				'verbose_name_plural': 't\xe9my vo f\xf3re',
			},
		),
	]
