# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import django.db.models.deletion
from django.conf import settings
import rich_editor.fields
import autoimagefield.fields


class Migration(migrations.Migration):

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='Article',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(verbose_name='vytvoren\xe9', editable=False)),
				('updated', models.DateTimeField(verbose_name='upraven\xe9', editable=False)),
				('title', models.CharField(max_length=255, verbose_name='n\xe1zov')),
				('slug', models.SlugField(unique=True, verbose_name='skratka URL')),
				('original_perex', rich_editor.fields.RichTextOriginalField(verbose_name='text na titulnej str\xe1nke', property_name='perex', filtered_field='filtered_perex')),
				('filtered_perex', rich_editor.fields.RichTextFilteredField(editable=False)),
				('original_annotation', rich_editor.fields.RichTextOriginalField(verbose_name='text pred telom \u010dl\xe1nku', property_name='annotation', filtered_field='filtered_annotation')),
				('filtered_annotation', rich_editor.fields.RichTextFilteredField(editable=False)),
				('original_content', rich_editor.fields.RichTextOriginalField(verbose_name='obsah', property_name='content', filtered_field='filtered_content')),
				('filtered_content', rich_editor.fields.RichTextFilteredField(editable=False)),
				('authors_name', models.CharField(max_length=255, verbose_name='meno autora')),
				('pub_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\u010das publik\xe1cie')),
				('published', models.BooleanField(default=False, verbose_name='publikovan\xe9')),
				('top', models.BooleanField(default=False, verbose_name='hodnotn\xfd \u010dl\xe1nok')),
				('image', autoimagefield.fields.AutoImageField(upload_to='article/thumbnails', verbose_name='obr\xe1zok', blank=True)),
				('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='autor', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
			],
			options={
				'verbose_name': '\u010dl\xe1nok',
				'verbose_name_plural': '\u010dl\xe1nky',
			},
		),
		migrations.CreateModel(
			name='Category',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('name', models.CharField(max_length=255, verbose_name='n\xe1zov')),
				('slug', models.SlugField(unique=True, verbose_name='skratka URL')),
				('description', models.TextField(verbose_name='popis')),
			],
			options={
				'verbose_name': 'kateg\xf3ria',
				'verbose_name_plural': 'kateg\xf3rie',
			},
		),
		migrations.AddField(
			model_name='article',
			name='category',
			field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='kateg\xf3ria', to='article.Category'),
		),
	]
