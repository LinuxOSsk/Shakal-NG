# -*- coding: utf-8 -*-
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
		migrations.CreateModel(
			name='News',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(editable=False)),
				('updated', models.DateTimeField(editable=False)),
				('title', models.CharField(max_length=255)),
				('slug', django_autoslugfield.fields.AutoSlugField(title_field='title', unique=True)),
				('original_short_text', rich_editor.fields.RichTextOriginalField(max_length=3000, property_name='short_text', filtered_field='filtered_short_text')),
				('filtered_short_text', rich_editor.fields.RichTextFilteredField(editable=False)),
				('original_long_text', rich_editor.fields.RichTextOriginalField(property_name='long_text', filtered_field='filtered_long_text')),
				('filtered_long_text', rich_editor.fields.RichTextFilteredField(editable=False)),
				('authors_name', models.CharField(max_length=255)),
				('source', models.CharField(max_length=100, blank=True)),
				('source_url', models.URLField(max_length=1000, blank=True)),
				('approved', models.BooleanField(default=False)),
				('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
				('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='news.Category')),
			],
			options={
				'verbose_name': 'spr\xe1va',
				'verbose_name_plural': 'spr\xe1vy',
			},
		),
	]
