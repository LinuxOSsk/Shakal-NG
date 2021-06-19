# -*- coding: utf-8 -*-
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
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(editable=False)),
				('updated', models.DateTimeField(editable=False)),
				('title', models.CharField(max_length=255)),
				('slug', models.SlugField(unique=True)),
				('original_perex', rich_editor.fields.RichTextOriginalField(property_name='perex', filtered_field='filtered_perex')),
				('filtered_perex', rich_editor.fields.RichTextFilteredField(editable=False)),
				('original_annotation', rich_editor.fields.RichTextOriginalField(property_name='annotation', filtered_field='filtered_annotation')),
				('filtered_annotation', rich_editor.fields.RichTextFilteredField(editable=False)),
				('original_content', rich_editor.fields.RichTextOriginalField(property_name='content', filtered_field='filtered_content')),
				('filtered_content', rich_editor.fields.RichTextFilteredField(editable=False)),
				('authors_name', models.CharField(max_length=255)),
				('pub_time', models.DateTimeField(default=django.utils.timezone.now)),
				('published', models.BooleanField(default=False)),
				('top', models.BooleanField(default=False)),
				('image', autoimagefield.fields.AutoImageField(upload_to='article/thumbnails', blank=True)),
				('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
			],
			options={
				'verbose_name': '\u010dl\xe1nok',
				'verbose_name_plural': '\u010dl\xe1nky',
			},
		),
		migrations.CreateModel(
			name='Category',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('name', models.CharField(max_length=255)),
				('slug', models.SlugField(unique=True)),
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
			field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='article.Category'),
		),
	]
