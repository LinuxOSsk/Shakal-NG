# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import rich_editor.fields
import autoimagefield.fields


class Migration(migrations.Migration):

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='Desktop',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(verbose_name='vytvoren\xe9', editable=False)),
				('updated', models.DateTimeField(verbose_name='upraven\xe9', editable=False)),
				('title', models.CharField(max_length=255, verbose_name='n\xe1zov')),
				('image', autoimagefield.fields.AutoImageField(upload_to='desktops', verbose_name='desktop')),
				('original_text', rich_editor.fields.RichTextOriginalField(max_length=10000, verbose_name='popis', property_name='text', filtered_field='filtered_text')),
				('filtered_text', rich_editor.fields.RichTextFilteredField(editable=False)),
				('author', models.ForeignKey(related_name='my_desktops', verbose_name='autor', to=settings.AUTH_USER_MODEL)),
			],
			options={
				'verbose_name': 'desktop',
				'verbose_name_plural': 'desktopy',
			},
		),
		migrations.CreateModel(
			name='FavoriteDesktop',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(verbose_name='vytvoren\xe9', editable=False)),
				('updated', models.DateTimeField(verbose_name='upraven\xe9', editable=False)),
				('desktop', models.ForeignKey(verbose_name='desktop', to='desktops.Desktop')),
				('user', models.ForeignKey(verbose_name='pou\u017e\xedvate\u013e', to=settings.AUTH_USER_MODEL)),
			],
			options={
				'abstract': False,
			},
		),
		migrations.AddField(
			model_name='desktop',
			name='favorited',
			field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='desktops.FavoriteDesktop'),
		),
	]
